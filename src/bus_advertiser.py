import dbus
import dbus.mainloop.glib
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import ssl

try:
    from gi.repository import GObject
except ImportError:
    import gobject as GObject



from bluez_ import *

mainloop = None

auth = {
  'username':"airchip1",
  'password':"yildiz2013"
}

tls = {
  'ca_certs':"/etc/ssl/certs/ca-certificates.crt",
}    
    
class PushMqttMessage(Characteristic):
    PUSH_UUID = '12345678-1234-5678-1234-56789abc000'
    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index,
            self.PUSH_UUID,
            ['read', 'write'],
            service)
        self.value = 13

    def ReadValue(self, options):
        print("Data reading from Center BLE Device")
        return self.value

    def WriteValue(self, value, options):
        print("Sending data from Center BLE Device to Server\n")
        print('Value: '+value+'\tValue Type: '+type(value)+'\n')
        publish.single("test",payload=str(value),hostname="mqtt.airchip.com.tr",client_id="bus1",auth=auth,tls=tls,port=8883,protocol=mqtt.MQTTv311)
        self.value = value   
        
class BusService(Service):
    BUS_SRV_UUID = '12345678-1234-5678-1234-56789abc0010'
    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.BUS_SRV_UUID, True)
        self.add_characteristic(PushMqttMessage(bus, 0, self))

class BusApplication(Application):
    def __init__(self, bus):
        Application.__init__(self, bus)
        self.add_service(BusService(bus, 0))


class BusAdvertisement(Advertisement):
    def __init__(self, bus, index):
        Advertisement.__init__(self, bus, index, 'peripheral')
        self.add_service_uuid(BusService.BUS_SRV_UUID)
        self.include_tx_power = True

def register_ad_cb():
    """
    Callback if registering advertisement was successful
    """
    print('Advertisement registered')


def register_ad_error_cb(error):
    """
    Callback if registering advertisement failed
    """
    print('Failed to register advertisement: ' + str(error))
    mainloop.quit()


def register_app_cb():
    """
    Callback if registering GATT application was successful
    """
    print('GATT application registered')


def register_app_error_cb(error):
    """
    Callback if registering GATT application failed.
    """
    print('Failed to register application: ' + str(error))
    mainloop.quit()


def main():
    global mainloop
    global display

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    bus = dbus.SystemBus()

    # Get ServiceManager and AdvertisingManager
    service_manager = get_service_manager(bus)
    ad_manager = get_ad_manager(bus)

    # Create gatt services
    app = BusApplication(bus)

    # Create advertisement
    test_advertisement = BusAdvertisement(bus, 0)

    mainloop = GObject.MainLoop()

    # Register gatt services
    service_manager.RegisterApplication(app.get_path(), {},
                                        reply_handler=register_app_cb,
                                        error_handler=register_app_error_cb)

    # Register advertisement
    ad_manager.RegisterAdvertisement(test_advertisement.get_path(), {},
                                     reply_handler=register_ad_cb,
                                     error_handler=register_ad_error_cb)

    try:
        mainloop.run()
    except KeyboardInterrupt:
        display.clear()
        display.write_display()


if __name__ == '__main__':
    main()
