#!/usr/bin/env python3
import argparse, time, sys
import pymysql

parser = argparse.ArgumentParser()
parser.add_argument("--host", default="localhost")
parser.add_argument("--port", type=int, default=3306)
parser.add_argument("--user", default="root")
parser.add_argument("--password", default="")
parser.add_argument("--database", default=None)
parser.add_argument("--timeout", type=int, default=60)  # Aumentado a 60 segundos
args = parser.parse_args()

start = time.time()
attempt = 0

print(f"🔍 Esperando MySQL en {args.host}:{args.port} (timeout: {args.timeout}s)...")

while True:
    attempt += 1
    elapsed = time.time() - start
    
    try:
        conn = pymysql.connect(
            host=args.host, port=args.port,
            user=args.user, password=args.password,
            database=args.database if args.database else None,
            connect_timeout=5
        )
        conn.close()
        print(f"✅ MySQL disponible después de {elapsed:.1f}s y {attempt} intentos.")
        sys.exit(0)
    except Exception as e:
        if elapsed > args.timeout:
            print(f"❌ Timeout esperando MySQL después de {elapsed:.1f}s: {str(e)}", file=sys.stderr)
            sys.exit(1)
        
        if attempt % 5 == 0:  # Log cada 5 intentos
            print(f"⏳ Intento {attempt}, {elapsed:.1f}s: {str(e)}")
        
        time.sleep(2)  # Aumentar sleep a 2 segundos
