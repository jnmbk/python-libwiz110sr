# WIZNET WIZ110SR Device Configuration Library
You can configure your Wiznet wiz110sr device using this Python library.
## Example Usage
Following example would change ip address setting on first device in your network

    import wiz110sr

    finder = wiz110sr.DeviceFinder()
    finder.search()
    device_list = finder.get_device_list()
    if device_list:
        print "Found devices:", device_list
        my_device = device_list[0]
        my_device.set_ip_address("10.0.0.2")
        my_device.save_config()`
    else:
        print "No wiz110sr device was found on current network"

