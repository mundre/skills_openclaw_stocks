# Learned Patterns

Patterns observed over time. Update as more data accumulates.

## Price Patterns (Kellyville / NSW / Amber)

- Weekday evening peak: typically 16:00-20:00 AEDT
- Late night secondary peak: 21:00-01:00 (varies)
- Overnight trough: 01:00-05:00 (sometimes negative)
- Morning ramp: 06:00-09:00 (moderate)
- Midday solar glut: 10:00-14:00 (low/negative feed-in possible)

## Solar Patterns

- Summer peak: ~20kW for 6-8 hours = 120-160 kWh/day
- Autumn/Winter: ~15kW for 4-6 hours = 60-90 kWh/day
- Cloudy day: 30-50% of clear-sky estimate
- Battery full by: 10:00-11:00 (summer sunny), 13:00-14:00 (winter/cloudy)

## Decision Heuristics

1. If tomorrow sunny AND tonight peak >12c → aggressive (floor 5-10%)
2. If tomorrow cloudy AND tonight peak <10c → conservative (floor 35-40%)
3. If 3+ rainy days ahead → very conservative (floor 50%)
4. If negative spot price → always charge regardless of SoC
5. Friday/Saturday nights tend to have lower peaks than Tue-Thu
