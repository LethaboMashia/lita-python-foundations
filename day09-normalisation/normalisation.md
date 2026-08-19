# The Normalisation Walk

## Starting point — bookings_raw (un-normalised)

| booking_id | client_name | client_city | services_booked | stylist_id | stylist_name |
|---|---|---|---|---|---|
| 1 | Naledi | Pretoria | Photo, Video | S2 | Thabo |

## 1NF — atomic cells

| booking_id | client_name | client_city | service | stylist_id | stylist_name |
|---|---|---|---|---|---|
| 1 | Naledi | Pretoria | Photo | S2 | Thabo |
| 1 | Naledi | Pretoria | Video | S2 | Thabo |
A cell must be atomic because if it holds more than one value, the database can't read each value individually, so I need to give each atomic value its own row.
## 2NF — remove partial dependencies

### bookings (key: booking_id)
| booking_id | client_name | client_city | stylist_id | stylist_name |
|---|---|---|---|---|
| 1 | Naledi | Pretoria | S2 | Thabo |
I moved client_name, client_city, stylist_id, and stylist_name into their own table because they only depend on booking_id, not on service — so storing them once per booking, instead of once per service, removes the duplication.
### booking_services (key: booking_id + service)
| booking_id | service |
|---|---|
| 1 | Photo |
| 1 | Video |

## 3NF — remove transitive dependencies
I moved stylist_name and client_city out because they depend on the stylist/client, not the booking — leaving them in bookings would mean the same name/city gets copied on every booking that person has, and if it ever changed, every copy would need updating. Giving clients their own client_id fixes the fragile client_name-as-identifier problem too, since two clients could share a name.

### clients (key: client_id)
| client_id | client_name | client_city |
|---|---|---|
| C1 | Naledi | Pretoria |

### stylists (key: stylist_id)
| stylist_id | stylist_name |
|---|---|
| S2 | Thabo |

### bookings (key: booking_id)
| booking_id | client_id | stylist_id |
|---|---|---|
| 1 | C1 | S2 |

### booking_services (key: booking_id + service) — unchanged from 2NF
| booking_id | service |
|---|---|
| 1 | Photo |
| 1 | Video |