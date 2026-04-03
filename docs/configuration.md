# ezfetch Configuration Guide

This document explains how to configure ezfetch using its JSON config file and CLI options, with usage examples.

---

## Table of Contents
- [Config File Location](#config-file-location)
- [Config File Structure](#config-file-structure)
- [Customizing Output](#customizing-output)
- [Themes](#themes)
- [Enabling/Disabling Fields](#enablingdisabling-fields)
- [Performance Options](#performance-options)
- [Example Configurations](#example-configurations)

---

## Config File Location
- The config file is located at `~/.config/ezfetch/config.json` (created on first run).

---

## Config File Structure
```json
{
  "display": {
    "show_logo": true,
    "show_colors": true,
    "truncate_length": 50,
    "show_color_blocks": true
  },
  "theme": {
    "name": "default"
  },
  "fields": {
    "enabled": ["User","Host","OS","Kernel","Uptime","Packages","Shell","Resolution","DE","WM","Terminal","CPU","GPU","Memory","Swap","Disk","Local IP","Battery","Locale"],
    "hide_unavailable": true,
    "hide_unknown": false
  },
  "performance": {
    "cache_enabled": true,
    "cache_duration": 300
  }
}
```

---

## Customizing Output
- Change `show_logo` to `false` to hide the ASCII logo.
- Set `show_colors` to `false` for monochrome output.
- Adjust `truncate_length` to control field value length.
- Set `show_color_blocks` to `false` to hide the color palette.

---

## Themes
- Available themes: `default`, `nord`, `dracula`, `gruvbox`, `monokai`, `solarized`
- Change the theme by setting `"name": "dracula"` (or any theme name).

---

## Enabling/Disabling Fields
- Edit the `enabled` list to show only specific fields.
- Example: To show only OS and CPU:
  ```json
  "enabled": ["OS", "CPU"]
  ```

---

## Performance Options
- `cache_enabled`: Set to `false` to disable caching.
- `cache_duration`: Time in seconds to keep cached data (default: 300).

---

## Example Configurations

### Minimal Output
```json
{
  "display": {"show_logo": false, "show_colors": false},
  "fields": {"enabled": ["OS", "CPU"]}
}
```

### Custom Theme and Fields
```json
{
  "theme": {"name": "gruvbox"},
  "fields": {"enabled": ["User", "Host", "OS", "Memory"]}
}
```

---

For more, see the [main README](../README.md).
