#!/usr/local/bin/python3

import json
import pathlib
import sys
import teslapy
from teslapy import Tesla, Vehicle, Battery

def handle_vehicle(v, cmd, cfg):
    if cmd == 'off':
        flag = 'enabled_' + v['display_name']
        if flag in cfg:
            charge_off_enabled = cfg[flag]
        else:
            charge_off_enabled = False;
            
        if charge_off_enabled is True and v.available() is True:
            data = v.get_vehicle_data()

            at_home = True
            drive_state = data['drive_state']
            if 'latitude' in drive_state and 'longitude' in drive_state:
                la_diff = abs(drive_state['latitude'] - cfg['home_lat'])
                lo_diff = abs(drive_state['longitude'] - cfg['home_lon'])
                if la_diff <= float(0.05) and lo_diff <= float(0.05):
                    at_home = True
                else:
                    at_home = False
            else:
                print('Faking at_home for ' + v['display_name'])

            charge_state = data['charge_state']
            if 'charging_state' not in charge_state:
                charge_status = 'Charging'
                print('Faking charge_status for ' + v['display_name'])
            else:
                charge_status = charge_state['charging_state']

            if at_home is True and charge_status == 'Charging':
                print('Stop charging ' + v['display_name'])
                x = v.command('STOP_CHARGE')
            else:
                if at_home is False:
                    print(v['display_name'] + ' is not at home')
                else:
                    print(v['display_name'] + ' is not charging')
        else:
            print(v['display_name'] + ' is ' + v['state'])
    else:
        print(v['display_name'] + ' is ' + v['state'])

def handle_battery(b, cmd, cfg):
    site_info = b.api('SITE_CONFIG')['response']
    current_reserve = site_info['backup_reserve_percent']
    if cmd == 'status':
        print('Powerwall Standby Reserve %d' % current_reserve)
    elif cfg['enabled_powerwall'] is True:
        target_reserve = cfg[cmd + '_backup_reserve_percent']
        if (target_reserve is not None and float(target_reserve) != current_reserve):
            print('Setting Powerwall Standby Reserve to ' + target_reserve)
            b.set_backup_reserve_percent(target_reserve)
        else:
            print('No change to Standby Reserve')
    else:
        print('Disabled')

def main():
    f = open("/usr/local/etc/tesla_api/charge-tesla.json", "r")
    cfg = json.loads(f.read())
    f.close()

    if len(sys.argv) == 2:
        cmd = sys.argv[1]
    else:
        cmd = "status"

    with Tesla(email = cfg['email'],
               retry = 5,
               cache_file = '/usr/local/etc/tesla_api/teslapy-cache.json'
               ) as tesla:

        if not tesla.authorized:
            print('Not authorised')
            if cmd == 'status':
                tesla.refresh_token(refresh_token=input('Enter SSO refresh token: '))

        if tesla.authorized:
            prod = tesla.battery_list() + tesla.vehicle_list()
            for i, product in enumerate(prod):
                if isinstance(product, Vehicle):
                    handle_vehicle(product, cmd, cfg)
                elif isinstance(product, Battery):
                    handle_battery(product, cmd, cfg)
        else:
            print('Not authorised :(')

if __name__ == "__main__":
    main()
