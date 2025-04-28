# celestial_basic
celestial_basic is a small light-weight CLI "program" that shows the current time, sunrise, and sunset at your location.
to use, you need to install the `astral` using `pip`.
```pip install astral```
you can then run the program like you would any other python program:
```py dir/to/file/celestial_basic.py```
celestial_basic also caches fetched data regarding your location, so it doesn't have to fetch it again.
to make sure the data is cached properly, the **working directory** of the CLI should be the same as the file location.