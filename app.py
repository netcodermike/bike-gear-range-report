from math import isfinite


def analyze(data):
    chainrings, sprockets = data["chainrings"], data["sprockets"]
    wheel, cadence = data["wheelMeters"], data["cadenceRpm"]
    if any(not isinstance(cogs, list) or not 1 <= len(cogs) <= 50 or
           any(type(cog) is not int or not 1 <= cog <= 200 for cog in cogs) for cogs in (chainrings, sprockets)):
        raise ValueError("Provide 1 to 50 tooth counts per list, sized from 1 to 200")
    if any(type(value) not in (int, float) or not isfinite(value) or value <= 0 for value in (wheel, cadence)):
        raise ValueError("Wheel rollout and cadence must be finite and positive")
    ratios = sorted((front / rear, front, rear) for front in chainrings for rear in sprockets)
    low, high = ratios[0][0], ratios[-1][0]
    speed = wheel * cadence * .06
    return {"lowestKmh": round(low * speed, 2), "highestKmh": round(high * speed, 2),
            "gearCount": len(ratios), "rangePercent": round(100 * high / low, 2),
            "gears": [{"chainring": front, "sprocket": rear, "ratio": round(ratio, 4),
                       "gearMeters": round(wheel * ratio, 3), "kmh": round(ratio * speed, 2),
                       "jumpPercent": round(100 * (ratio / ratios[index - 1][0] - 1), 2) if index else None}
                      for index, (ratio, front, rear) in enumerate(ratios)]}

if __name__ == "__main__":
    import json
    from pathlib import Path
    import sys
    try:
        path, = sys.argv[1:]
        result = analyze(json.loads(Path(path).read_text(encoding="utf-8")))
        print(json.dumps(result, ensure_ascii=True, allow_nan=False))
    except (OSError, ValueError, TypeError, KeyError, AttributeError, OverflowError) as error:
        print(f"Invalid input: {error}", file=sys.stderr)
        sys.exit(2)
