from zeroconf import Zeroconf, ServiceBrowser, ServiceStateChange

def on_service_state_change(zeroconf, service_type, name, state_change):
    if state_change is ServiceStateChange.Added:
        info = zeroconf.get_service_info(service_type, name)
        if info is not None:
            print("Service added:", name)
            print("  Host:", info.server.decode("utf-8"))
            print("  Port:", info.port)
            print("  IP Address:", info.parsed_addresses)

def main():
    zeroconf = Zeroconf()
    browser = ServiceBrowser(zeroconf, "_ipp._tcp.local.", handlers=[on_service_state_change])

    try:
        input("Press Enter to stop...")
    except KeyboardInterrupt:
        pass
    
    finally:
        zeroconf.close()

if __name__ == "__main__":
    main()
