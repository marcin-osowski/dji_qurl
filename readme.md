# DJI drone firmware URL extractor

### Get URLs for DJI firmware

This script dumps all `QUrl.toString()` return values from a running
DJI Assistant 2 for Windows (`DJIService.exe`). This happens to be just
enough to cover all firmware URLs that are retrieved during a firmware
update. You'll have to manually try to `wget` some of the printed URLs,
as DJIService.exe accesses a lot more URLs than just those
with firmware images.

**This is a hack that messes with DJI's software and can easily crash it. If your drone dies mid-flash, or some other calamity happens, it's not my problem.** It worked just fine for me, though.

