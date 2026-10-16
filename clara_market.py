"""Pemantau IHSG dan saham BEI berbasis data pasar + Google News RSS.
Sinyal adalah heuristik, bukan prediksi pasti atau saran beli/jual personal.
"""
from __future__ import annotations
import math, re, time, xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any
import requests

INDEX_SYMBOL = "^JKSE"
DEFAULT_WATCHLIST = ["BBCA.JK","BBRI.JK","BMRI.JK","TLKM.JK","ASII.JK","ICBP.JK","AMRT.JK","ANTM.JK","MDKA.JK","GOTO.JK","UNVR.JK","CPIN.JK"]
YAHOO_CHART = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
NEWS_RSS = "https://news.google.com/rss/search?q={query}&hl=id&gl=ID&ceid=ID:id"
POSITIVE = ("naik", "menguat", "laba naik", "laba bersih meningkat", "dividen", "buyback", "kontrak baru", "akuisisi", "ekspansi", "rekor laba", "target harga naik", "rebound", "outlook positif", "upgrade")
NEGATIVE = ("turun", "melemah", "rugi", "laba turun", "utang meningkat", "gagal bayar", "sanksi", "denda", "investigasi", "disuspensi", "downgrade", "outlook negatif", "anjlok", "PHK", "kebangkrutan", "pailit")


def _clean_symbol(symbol: str) -> str:
    s=(symbol or "").strip().upper().replace(" ","")
    if s in ("IHSG","IDX","COMPOSITE","^JKSE"): return INDEX_SYMBOL
    if re.fullmatch(r"[A-Z]{4}",s): s += ".JK"
    if not re.fullmatch(r"(?:\^[A-Z0-9.^=-]+|[A-Z0-9.-]+\.JK)",s): raise ValueError("Kode saham tidak valid. Gunakan contoh BBCA.JK atau ^JKSE.")
    return s


def _history_stats(closes: list[float], volumes: list[float]) -> dict[str, float]:
    def ret(n):
        if len(closes) <= n or closes[-n-1] == 0: return 0.0
        return (closes[-1] / closes[-n-1] - 1.0) * 100
    returns=[(closes[i]/closes[i-1]-1) for i in range(1,len(closes)) if closes[i-1]]
    vol=(sum((x-(sum(returns)/len(returns)))**2 for x in returns)/max(1,len(returns)-1))**0.5*100 if len(returns)>1 else 0.0
    vavg=sum(volumes[-20:])/max(1,len(volumes[-20:])) if volumes else 0
    vr=volumes[-1]/vavg if volumes and vavg else 1.0
    return {"return_5d":ret(5),"return_20d":ret(20),"return_60d":ret(60),"volatility_daily_pct":vol,"volume_ratio":vr}


def fetch_quote(symbol: str, session=requests, timeout: int=12) -> dict[str, Any]:
    sym=_clean_symbol(symbol)
    url=YAHOO_CHART.format(symbol=requests.utils.quote(sym,safe=""))
    r=session.get(url,params={"range":"6mo","interval":"1d","events":"div,splits"},headers={"User-Agent":"Mozilla/5.0 ClaraDesktopBuddy/3"},timeout=timeout)
    r.raise_for_status(); body=r.json()
    chart=body.get("chart",{}); err=chart.get("error")
    result=(chart.get("result") or [None])[0]
    if not result: raise RuntimeError((err or {}).get("description") or "Data harga tidak tersedia.")
    meta=result.get("meta") or {}; q=((result.get("indicators") or {}).get("quote") or [{}])[0]
    closes=[float(x) for x in (q.get("close") or []) if x is not None]
    volumes=[float(x) for x in (q.get("volume") or []) if x is not None]
    if not closes: raise RuntimeError("Provider tidak mengembalikan histori penutupan.")
    last=float(meta.get("regularMarketPrice") or closes[-1])
    prev=float(meta.get("chartPreviousClose") or meta.get("previousClose") or (closes[-2] if len(closes)>1 else last))
    ts=meta.get("regularMarketTime") or (result.get("timestamp") or [0])[-1]
    stamp=datetime.fromtimestamp(ts,timezone.utc).astimezone().isoformat(timespec="minutes") if ts else "Waktu provider tidak tersedia"
    return {"symbol":sym,"name":meta.get("longName") or meta.get("shortName") or sym,"currency":meta.get("currency","IDR"),"price":last,"previous_close":prev,"change":last-prev,"change_pct":(last/prev-1)*100 if prev else 0,"day_low":meta.get("regularMarketDayLow"),"day_high":meta.get("regularMarketDayHigh"),"timestamp":stamp,"provider":"Yahoo Finance (kuotasi dapat tertunda)",**_history_stats(closes,volumes)}


def fetch_news(query: str="IHSG saham Indonesia BEI", session=requests, timeout: int=12, max_items:int=15) -> list[dict[str,Any]]:
    url=NEWS_RSS.format(query=requests.utils.quote(query))
    r=session.get(url,headers={"User-Agent":"Mozilla/5.0 ClaraDesktopBuddy/3"},timeout=timeout); r.raise_for_status()
    root=ET.fromstring(r.content); out=[]
    for item in root.findall(".//item")[:max_items]:
        title=(item.findtext("title") or "").strip(); link=(item.findtext("link") or "").strip(); pub=(item.findtext("pubDate") or "").strip()
        source=item.find("source"); publisher=(source.text.strip() if source is not None and source.text else "Google News RSS")
        try: dt=parsedate_to_datetime(pub).astimezone().isoformat(timespec="minutes")
        except Exception: dt=pub or "Tanggal tidak tersedia"
        if title: out.append({"title":title,"url":link,"published":dt,"publisher":publisher,"sentiment":headline_sentiment(title)})
    return out


def headline_sentiment(text: str) -> int:
    s=(text or "").casefold()
    p=sum(1 for x in POSITIVE if x in s); n=sum(1 for x in NEGATIVE if x in s)
    return 1 if p>n else (-1 if n>p else 0)


def signal_for_quote(q: dict[str,Any], headlines: list[dict[str,Any]]) -> dict[str,Any]:
    sym=q.get("symbol","").replace(".JK","")
    relevant=[h for h in headlines if sym and (sym.casefold() in h["title"].casefold() or q.get("name","").casefold() in h["title"].casefold())]
    sentiment=(sum(h["sentiment"] for h in relevant)/len(relevant)) if relevant else 0.0
    # Clip momentum input so a single extreme day cannot dominate; sentiment is weak evidence.
    r5=max(-15,min(15,float(q.get("return_5d",0))))/15
    r20=max(-30,min(30,float(q.get("return_20d",0))))/30
    score=0.42*r5+0.33*r20+0.25*sentiment
    if not relevant: score*=0.8
    if q.get("volatility_daily_pct",0)>5: score*=0.75
    if score>=0.28: stance="Momentum positif — pantau peluang"
    elif score<=-0.28: stance="Momentum negatif — waspadai risiko"
    else: stance="Netral / belum cukup konfirmasi"
    if abs(score)>=0.58 and relevant: confidence="Sedang (indikator terbatas)"
    elif abs(score)>=0.28: confidence="Rendah–sedang"
    else: confidence="Rendah"
    daily="Bullish" if q.get("change_pct",0)>1 and q.get("return_5d",0)>0 else ("Bearish" if q.get("change_pct",0)<-1 and q.get("return_5d",0)<0 else "Campuran")
    monthly="Bullish" if q.get("return_20d",0)>3 and q.get("return_60d",0)>0 else ("Bearish" if q.get("return_20d",0)<-3 and q.get("return_60d",0)<0 else "Campuran")
    return {"symbol":q.get("symbol"),"score":score,"stance":stance,"confidence":confidence,"daily_bias":daily,"monthly_bias":monthly,"matched_headlines":relevant,"reasoning":f"Return 5 hari {q.get('return_5d',0):+.2f}%; 20 hari {q.get('return_20d',0):+.2f}%; sentimen judul terkait {sentiment:+.2f}; volatilitas harian {q.get('volatility_daily_pct',0):.2f}%"}


def analysis_summary(quotes: list[dict[str,Any]], headlines: list[dict[str,Any]]) -> list[dict[str,Any]]:
    return sorted([signal_for_quote(q,headlines) for q in quotes],key=lambda s:s['score'],reverse=True)
