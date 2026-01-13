#!/usr/bin/env python3
"""CLI helper to call the local /predict endpoint.

Usage examples:
  python src/cli_predict.py --city Colombo
  python src/cli_predict.py --lat 6.9271 --lon 79.8612
  python src/cli_predict.py --features 2026 1 27.5 70 2.0
"""
import sys
import argparse
import json
import requests


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--city', help='City or district name')
    p.add_argument('--lat', type=float, help='Latitude')
    p.add_argument('--lon', type=float, help='Longitude')
    p.add_argument('--population', type=int, help='Population (optional)')
    p.add_argument('--features', nargs=5, help='Five features: year month temp humidity rainfall', type=float)
    p.add_argument('--url', default='http://127.0.0.1:5000/predict', help='Prediction endpoint')
    args = p.parse_args()

    payload = {}
    if args.features:
        payload['features'] = args.features
    else:
        if args.city:
            payload['city'] = args.city
        if args.lat is not None and args.lon is not None:
            payload['lat'] = args.lat
            payload['lon'] = args.lon
        if args.population:
            payload['population'] = args.population

    if not payload:
        print('Provide either --features or --city or --lat/--lon')
        sys.exit(2)

    try:
        r = requests.post(args.url, json=payload, timeout=15)
    except Exception as e:
        print('Request failed:', e)
        sys.exit(1)

    try:
        data = r.json()
    except Exception:
        print('Non-JSON response:', r.text)
        sys.exit(1)

    print('Status:', r.status_code)
    print(json.dumps(data, indent=2))


if __name__ == '__main__':
    main()
