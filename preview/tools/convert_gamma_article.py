#!/usr/bin/env python3
"""Convert authenticated Gamma read_gamma HTML to a safe, English HTML fragment.

Input is a locally saved *authenticated* read_gamma text response, not a public
Gamma URL. This script never writes to existing website articles.
"""
import argparse
import html
from html.parser import HTMLParser
from pathlib import Path

ALLOWED = {"h1","h2","h3","h4","p","b","strong","i","em","ul","ol","li","blockquote","a","hr"}
VOID = {"hr"}
class Extract(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth=0; self.out=[]; self.stack=[]; self.title_count=0
    def handle_starttag(self,tag,attrs):
        if tag=="section": self.depth+=1
        if self.depth<1: return
        if tag not in ALLOWED: return
        if tag=="h1":
            self.title_count+=1
            if self.title_count>1: tag="h2"
        if tag=="a":
            href=dict(attrs).get("href","")
            if not href.startswith(("https://","http://","#")): href=""
            self.out.append('<a href="'+html.escape(href,quote=True)+'" rel="noopener noreferrer">')
        else: self.out.append("<"+tag+">")
        if tag not in VOID:self.stack.append(tag)
    def handle_endtag(self,tag):
        if self.depth>0 and tag in ALLOWED and tag not in VOID:
            if self.stack and (self.stack[-1]==tag or (tag=="h1" and self.stack[-1]=="h2")):
                self.out.append("</"+self.stack.pop()+">")
        if tag=="section" and self.depth>0:self.depth-=1
    def handle_data(self,data):
        if self.depth>0:self.out.append(html.escape(data))
def convert(raw):
    start=raw.find("<div><section")
    if start<0: raise ValueError("Gamma article sections not found")
    p=Extract();p.feed(raw[start:])
    out="".join(p.out)
    if p.title_count<1 or len(out)<500: raise ValueError("Missing article title or unexpectedly short content")
    return '<article class="gamma-english-article" lang="en">\n'+out+'\n</article>\n'
def main():
    ap=argparse.ArgumentParser();ap.add_argument("input");ap.add_argument("--output",required=True)
    a=ap.parse_args();source=Path(a.input);target=Path(a.output)
    if target.exists():raise SystemExit("Refusing to overwrite existing file: "+str(target))
    target.write_text(convert(source.read_text(encoding="utf-8")),encoding="utf-8")
    print("Dry-run fragment written:",target)
if __name__=="__main__":main()
