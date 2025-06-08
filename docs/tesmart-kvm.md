# TESMART KVM switch + PiKVM

I found [these docs](https://docs.pikvm.org/tesmart/) to work quite well. However, there were a few problems I ran into while configuring this switch to work with PiKVM.

For starters, the switch comes pre-programmed to a fixed IP address (`192.168.1.10` -- which will work if you use `192.168.1.1/24` on your home network). If you're like me, I use `10.x.y.z` for things and so I had to reset the switch's IP by using the LAN interface and the TESMART Controller software. The docs above link to a TESMART Downloads Page (which was unavailable to me). Luckily, I was able to do some digging and found [this page](https://support.tesmart.com/hc/en-us/articles/10271501164953-LAN-RS232-Control-Software) which had `16x1-HDMI-Switch-Controler.rar` (yes, it's misspelled). Unfortunately, I ran into some additional problems with this software on Windows 11; it was constantly complaining about missing `MSVCR110.DLL` (which I found [here](https://www.dll-files.com/msvcr110.dll.html)). Once I copied that `.dll` into the same directory as the controller software, things worked well.

You should be able to follow the rest of the [PiKVM docs](https://docs.pikvm.org/tesmart/) to get things working correctly. I also took an extra measure to reserve the IP address I assigned to the KVM switch in UniFi so it wasn't DHCP'd to something else accidentally.
