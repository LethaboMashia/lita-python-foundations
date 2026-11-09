# D17 Predictions (written before any code)

## Attack A: session guessing
Session IDs are incrementing integers (1, 2, 3…). If I log in and get session ID 7, I can change my cookie to 6, 5, 4… and see other users' dashboards. It works because the IDs are predictable — I don't need to guess, I just count. Logout only clears the cookie on the client side but does NOT delete the session on the server, so old session IDs stay valid even after a user "logs out." Any ID with a live server-side session will let me in.

**Predicted output:** the script walks IDs 1–20. For each ID that has an active session on the server, it will get a 200 response with "Welcome, <username>" and the dashboard HTML. For IDs with no session, it will get a redirect to /login or a "not logged in" message. If two users registered and logged in, I expect to see two hits out of 20.

## Attack B: username enumeration
The vulnerable app returns a different error for "bad username" versus "bad password." If I try the username "lethabo" with a wrong password and get "Invalid password," but try "fakeperson" and get "User not found," the app just told me which usernames exist. The script tries 10 usernames. Only "lethabo" and "phuti" are registered.

**Predicted output:** for "lethabo" and "phuti," the script will print something like "lethabo — EXISTS (got 'Invalid password' error)." For the other 8 fake names, it will print "fakename — DOES NOT EXIST (got 'User not found' error)." That gives me 2 confirmed usernames out of 10 tried.

## Attack C: brute force with a 10-word list
There is no attempt limit. The password list has 10 words and the real password is word 7 ("sunshine1"). The script tries each word in order against one username.

**Predicted output:** attempts 1–6 get "Invalid password" (or similar rejection). Attempt 7 ("sunshine1") succeeds — the server returns a 200 or a redirect to /dashboard with a valid session cookie. The script prints "SUCCESS on attempt 7: sunshine1" and stops. Total requests sent: 7 (it stops on success, doesn't try the remaining 3).

## Session fixation
In the vulnerable app, the session ID assigned before login is the SAME session ID used after login. It does not change. This matters because: if an attacker can set or know a victim's pre-login session ID (e.g. by sending them a link with a session cookie already set), the attacker already has that ID. When the victim logs in, that same ID now has full access to their account — the attacker walks in with the ID they already knew, no password needed.

**Predicted output:** if I print the session ID before logging in and again after logging in on the vulnerable app, both will be identical.

## Which defence stops which attack
- **Attack A (session guessing):** stopped by `secrets.token_urlsafe(32)` — the session ID is now a 32-byte random string instead of 1, 2, 3. You cannot guess or walk through them. Also helped by issuing a NEW session ID at login and deleting the old one on logout (server-side).
- **Attack B (username enumeration):** stopped by the single generic error message — "Invalid username or password" — regardless of whether the username or the password was wrong. The attacker gets the same response either way, so they cannot tell which usernames exist.
- **Attack C (brute force):** stopped by the lockout after 5 failed attempts for 60 seconds. The script sends 5 wrong passwords, and attempt 6 gets locked out. It never reaches attempt 7 where the real password is. Total requests that get a real yes/no answer: 5. After that, every request for 60 seconds gets "Account locked."

**Which attack might still partly work against the secure app:**
Attack B — partially. The generic error message hides WHICH input was wrong, but the app doesn't normalise response timing. A database lookup for a username that exists takes slightly longer than an immediate rejection for one that doesn't. An attacker measuring response times in milliseconds could still guess which usernames are real. This lab doesn't fix that timing side-channel.