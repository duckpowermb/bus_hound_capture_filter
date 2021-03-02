# bus_hound_capture_filter
a simple python script to filter bus_hound capture text file,help parsing device / parse / datas  
make it easy for futher process (e.g. data simulation)  

![](https://github.com/duckpowermb/bus_hound_capture_filter/blob/main/readme_assert/dems.png)


How to use:  
python bh_filter.py [-v] "inputfile"  


How it work:  
Here is the line parse process >  

step 1.Delete head/tail spaces, delete more than one space in the content  
step 2.Using regular expression to verify content format  
step 3.if verified,extract device/parse/datas  
step 4.format and print parse result  
