# Virtual Gas Meter Integration for Home Assistant

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]][license]
[![hacs][hacsbadge]][hacs]
[![Project Maintenance][maintenance-shield]][user_profile]
[![Buy me a coffee][buymecoffeebadge]][buymecoffee]

Estimate gas consumption from boiler runtime and keep it calibrated with real meter readings. Virtual Gas Meter creates a calculated gas meter that can be used in Home Assistant's Energy Dashboard without needing a smart gas meter.

The integration watches a boiler/heating entity, adds estimated gas usage while that entity is running, and lets you periodically enter a real physical meter reading so the average hourly usage rate stays accurate over time.

The integration exposes the following entities:

- **Virtual Gas Meter Total** — the cumulative virtual gas meter reading for Energy Dashboard use
- **Virtual Gas Meter Consumed Gas** — estimated gas consumed since the last real meter reading
- **Virtual Gas Meter Heating Interval** — boiler runtime since the last real meter reading

## Installation

### HACS Custom Repository (Recommended)

1. Make sure [HACS](https://hacs.xyz/) is installed in your Home Assistant instance.
2. Add this repository as a custom repository in HACS:
   - Go to HACS > Integrations > Three dots in the top right > Custom repositories
   - Add `https://github.com/Migz93/ha-virtual_gas_meter` with category "Integration"
3. Click "Install" on the Virtual Gas Meter integration.
4. Restart Home Assistant.

You can also use the My Home Assistant button:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Migz93&repository=ha-virtual_gas_meter&category=integration)

### Manual Installation

1. Download the latest release from the [GitHub repository](https://github.com/Migz93/ha-virtual_gas_meter).
2. Extract the contents.
3. Copy the `custom_components/virtual_gas_meter` folder to your Home Assistant's `custom_components` directory.
4. Restart Home Assistant.

## Configuration

### Adding the Integration

1. Go to **Settings** -> **Devices & Services**
2. Click **+ ADD INTEGRATION** and search for "Virtual Gas Meter"
3. Select the entity that represents your boiler or heating demand
4. Choose your unit system: `m3` or `CCF`
5. Enter your current physical meter reading
6. Enter an estimated average hourly consumption rate while the boiler is running

The boiler entity can be a `switch`, `binary_sensor`, `sensor`, or `climate` entity.

For `climate` entities, the integration treats the boiler as running when `hvac_action` is `heating`. For `sensor` entities, numeric values above zero are treated as running; the string `on` is also treated as running.

Only one Virtual Gas Meter config entry is supported.

### Options

After setup, go to **Settings** -> **Devices & Services** -> **Virtual Gas Meter** -> **Configure** to change:

| Setting                        | Description                                              |
| ------------------------------ | -------------------------------------------------------- |
| **Boiler Entity**              | The entity used to detect boiler runtime                 |
| **Average Hourly Consumption** | Estimated gas usage per hour while the boiler is running |

The unit system and initial meter reading are fixed after setup. To correct the real meter reading, use the calibration service below.

## Entities

- `sensor.vgm_total` — cumulative virtual meter reading, designed for the Energy Dashboard.
- `sensor.vgm_consumed_gas` — estimated gas consumed since the last real meter reading update.
- `sensor.vgm_heating_interval` — boiler runtime since the last real meter reading update.

The total sensor also includes calibration attributes such as the last real meter reading, last reading timestamp, average hourly rate, tracked boiler entity, and configured unit.

## Energy Dashboard

Use **Virtual Gas Meter Total** as your gas source:

1. Go to **Settings** -> **Dashboards** -> **Energy**
2. Click **Add Gas Source**
3. Select `sensor.vgm_total`
4. Configure your gas cost if desired

## Calibration Service

Use `virtual_gas_meter.real_meter_reading_update` when you have a new physical gas meter reading.

The service:

- Validates that the new reading is not lower than the previous real reading
- Snaps the virtual total to the new physical reading
- Resets consumed gas and heating interval
- Optionally recalculates the average hourly consumption rate from actual usage

### Service Fields

| Field                      | Required | Default | Description                                                       |
| -------------------------- | -------- | ------- | ----------------------------------------------------------------- |
| `meter_reading`            | Yes      |         | New physical gas meter reading in your configured unit            |
| `timestamp`                | No       | now     | Timestamp for the reading                                         |
| `recalculate_average_rate` | No       | `true`  | Whether to update the average rate from the actual usage observed |

### Examples

Recalibrate and update the average rate:

```yaml
action: virtual_gas_meter.real_meter_reading_update
data:
  meter_reading: 4447.816
```

Use a specific timestamp:

```yaml
action: virtual_gas_meter.real_meter_reading_update
data:
  meter_reading: 4447.816
  timestamp: "2026-04-30 15:51:00"
```

Snap the meter total without changing the average rate:

```yaml
action: virtual_gas_meter.real_meter_reading_update
data:
  meter_reading: 4447.816
  recalculate_average_rate: false
```

## How the Estimate Works

The integration estimates usage from boiler runtime and your configured average hourly consumption rate:

1. The configured boiler entity is watched for running/off transitions.
2. While running, the integration adds one minute of gas usage every 60 seconds.
3. Each minute adds `average_rate_per_h / 60` to consumed gas.
4. When the boiler turns off, a final one-minute tick is applied.
5. The total sensor reports `last_real_meter_reading + consumed_gas`.
6. When you enter a real reading, consumed gas and runtime reset to zero.

If recalculation is enabled during a real reading update, the new hourly rate is calculated from:

```text
(new_meter_reading - previous_real_meter_reading) / boiler_runtime_hours
```

This means accuracy improves when you occasionally enter real readings after the boiler has accumulated meaningful runtime.

## Notes & Limitations

- `CCF` support is available but less tested than `m3`.
- This is an estimate. Accuracy depends on how well your tracked boiler entity represents actual gas burn time.
- The integration does not read a physical meter automatically.
- The configured unit cannot be changed after setup.
- The new meter reading must be greater than or equal to the previous real reading.
- Calibrating monthly, or after a useful amount of boiler runtime, usually gives better results.

## Contributing

Contributions are welcome! Please read the [Contribution guidelines](CONTRIBUTING.md) before opening a pull request.

---

## AI-Assisted Development

> **Transparency Notice**
>
> This integration was developed with assistance from AI coding agents. While the codebase follows Home Assistant custom integration patterns and validation tooling, AI-generated code may not be reviewed or tested to the same extent as manually written code.
>
> If you encounter any issues, please [open an issue](https://github.com/Migz93/ha-virtual_gas_meter/issues) on GitHub.

---

## Credits

- This project is a fork of [Virtual Gas Meter](https://github.com/lukepatrick/virtual_gas_meter) by [@lukepatrick](https://github.com/lukepatrick)
- Which in turn is a fork of the original [Virtual Gas Meter](https://github.com/Elbereth7/virtual_gas_meter) by [@Elbereth7](https://github.com/Elbereth7)
- Integration maintained by [Migz93](https://github.com/migz93)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

[buymecoffee]: https://www.buymeacoffee.com/Migz93
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/Migz93/ha-virtual_gas_meter.svg?style=for-the-badge
[commits]: https://github.com/Migz93/ha-virtual_gas_meter/commits/main
[hacs]: https://hacs.xyz
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[license]: https://github.com/Migz93/ha-virtual_gas_meter/blob/main/LICENSE
[license-shield]: https://img.shields.io/github/license/Migz93/ha-virtual_gas_meter.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-Migz93-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/Migz93/ha-virtual_gas_meter.svg?style=for-the-badge
[releases]: https://github.com/Migz93/ha-virtual_gas_meter/releases
[user_profile]: https://github.com/Migz93
