# rpi-eboard
This project is control rgb-cooling-hat of yahboom with pyhton code.

## Requirements

Python packages are listed in `requirements.txt`:

- `psutil`
- `smbus2`
- `Pillow`
- `PyYAML`
- `adafruit-blinka`
- `adafruit-circuitpython-ssd1306`
- `RPi.GPIO`

`RPi.GPIO` is only needed if you use `lib/stepmotor.py` or other GPIO code.
The code now supports the modern `adafruit-blinka` +
`adafruit-circuitpython-ssd1306` stack on current Raspberry Pi OS images.

If you need the legacy Adafruit OLED stack on an older image, install these
manually as well:

```bash
pip install Adafruit-SSD1306 spidev adafruit-pureio
```

## Ubuntu 26.04 setup

1. Install system packages:

   ```bash
   sudo apt update
   sudo apt install -y python3 python3-venv i2c-tools
   ```

2. Enable I2C on the Pi and reboot:

   Add this line to `/boot/firmware/config.txt` if it is not already present:

   ```ini
   dtparam=i2c_arm=on
   ```

   After reboot, verify the bus with:

   ```bash
   i2cdetect -y 1
   ```

3. Create a virtual environment:

   ```bash
   cd /home/zane/git/rpi-eboard
   python3 -m venv .venv
   source .venv/bin/activate
   ```

4. Install Python dependencies:

   ```bash
   pip install -U pip
   pip install -r requirements.txt
   ```

5. Run the status script:

   ```bash
   python3 rpi_stats.py
   ```

   Make sure the virtual environment is active before running the script:

   ```bash
   which python3
   # should point to /home/zane/git/rpi-eboard/.venv/bin/python3
   ```

   If you get permission errors on `/dev/i2c-*`, run it with `sudo` first and
   then decide whether to add your user to the `i2c` group.

   On Ubuntu 26.04, do not install project packages into the system Python.
   Use the virtual environment created above. This avoids the
   `externally-managed-environment` error from PEP 668.

## Runtime notes

The main status script is `rpi_stats.py`. It shows CPU temperature, `eth0`
IP, `wlan0` IP, and adjusts the fan speed by temperature.

If Ubuntu uses predictable interface names, set `ETH_IFACE` and `WLAN_IFACE`
before launching the script:

```bash
ETH_IFACE=enp1s0 WLAN_IFACE=wlp1s0 python3 rpi_stats.py
```

If the OLED test prints `hardware OLED unavailable`, one of these is true:

1. Neither OLED driver stack is installed.
2. I2C is disabled or the process cannot access `/dev/i2c-1`.
3. The display is not at address `0x3c`.

If `Adafruit-SSD1306` fails to install on your image, use the modern stack
instead:

```bash
pip install adafruit-blinka adafruit-circuitpython-ssd1306
```

If you prefer the legacy stack, install the matching Debian packages and retry
the `pip install -r requirements.txt` step inside `.venv`.

If you see `ModuleNotFoundError` for `smbus2` or any other package, you are
almost certainly using the system Python instead of the virtual environment.

## OLED test

Use `oled_test.py` to check whether the display itself is still healthy:

```bash
python3 oled_test.py
```

To keep cycling patterns:

```bash
python3 oled_test.py --loop
```

The sequence includes clear, full-on, checkerboard, grid, text, diagonal, and
border patterns.

The test runs in two phases:

1. Targeted scan: clear, full-on, row scan, column scan, block scan
2. Visual scan: checkerboard, grid, text, diagonal, border

If the same rows or columns stay missing during the targeted scan, the panel
or its driver path is more likely at fault than the application code.

## RGB and fan tests

Use `rgb_test.py` to step through RGB brightness levels, individual channels,
and common colors:

```bash
python3 rgb_test.py
```

If your board does not like the per-channel mode, keep the default run and
avoid `--channels`:

```bash
python3 rgb_test.py --channels
```

Use `fan_test.py` to cycle fan states directly, or to drive the fan from CPU
temperature using the same threshold logic as `rpi_stats.py`:

```bash
python3 fan_test.py
python3 fan_test.py --live
```

For build failures, the usual fallback packages are:

```bash
sudo apt install -y python3-dev build-essential libjpeg-dev zlib1g-dev libfreetype6-dev
```
