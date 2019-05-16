1. settings for wsl, add options to /etc/wsl.conf 
```conf
automount]
enabled = true
options = "metadata,umask=0022"
```

this will  prevent word-writable warning when running ansible under wsl