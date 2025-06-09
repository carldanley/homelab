# Checking Synology SSD Cache

## Checking Write Cache

To check SSD Write caching speeds from the Synology, SSH into a console and perform the following command:

```bash
dd if=/dev/zero of=temp.txt bs=1M count=100
```

This should write a ~100MB file and give you an output regarding the speed at which the file was written.

## Checking Read Cache

To check SSD Read caching speeds from the Synology, SSH into a console and perform the following command:

```bash
dd if=/some/file/thats/new.txt of=/dev/null
```

This should read the file into `/dev/null` and give you an output regarding the speed at which the file was written.

If you re-run the same command above, you should see noticeably faster speeds since the file should have been added to the read cache.

## More Information

[SSD Cache](https://kb.synology.com/en-us/DSM/help/DSM/StorageManager/genericssdcache?version=7)
