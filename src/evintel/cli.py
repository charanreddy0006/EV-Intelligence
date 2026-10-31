import argparse
from .pipeline import run_pipeline
from .analytics import overview, city_performance

def main():
    parser = argparse.ArgumentParser(description="EV Intelligence data platform")
    parser.add_argument("command", choices=["run", "summary", "cities"])
    args = parser.parse_args()
    if args.command == "run":
        print(run_pipeline())
    elif args.command == "summary":
        print(overview())
    else:
        print(city_performance().to_string(index=False))

if __name__ == "__main__":
    main()
