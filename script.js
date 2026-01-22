 /* ======= Config ======= */
        const API = "http://127.0.0.1:5000"; // your Flask server

        /* ======= Splash → Login ======= */
        window.addEventListener('load', () => {
            show('splash');
            setTimeout(() => show('login'), 1800);
        });

        /* ======= Simple Router ======= */
        function show(id) {
            document.querySelectorAll('.screen, #app').forEach(el => el.classList.remove('show'));
            if (id === 'app') {
                document.getElementById('app').style.display = 'block';
            } else {
                document.getElementById('app').style.display = 'none';
            }
            const target = document.getElementById(id);
            if (target) { target.classList.add('show'); }
        }

        /* ======= Helpers ======= */
        function togglePass(id) {
            const f = document.getElementById(id);
            f.type = (f.type === 'password') ? 'text' : 'password';
        }

        function toast(msg, duration = 3000) {
            const toastEl = document.getElementById('toast');
            toastEl.textContent = msg;
            toastEl.classList.add('show');

            setTimeout(() => {
                toastEl.classList.remove('show');
            }, duration);
        }

        /* ======= Auth (wired to your backend) ======= */
        async function login() {
            const email = document.getElementById('loginEmail').value.trim();
            const password = document.getElementById('loginPass').value.trim();
            if (!email || !password) return toast('Enter email & password');

            try {
                const res = await fetch(API + '/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });
                const data = await res.json();
                if (data.success) {
                    show('app');
                } else {
                    toast(data.msg || 'Login failed');
                }
            } catch (e) {
                toast('Network error. Please try again.');
            }
        }

        async function signup() {
            const email = document.getElementById('suEmail').value.trim();
            const password = document.getElementById('suPass').value.trim();
            const confirm = document.getElementById('suConfirm').value.trim();
            if (!email || !password) return toast('Fill all fields');
            if (password !== confirm) return toast('Passwords do not match');

            try {
                const res = await fetch(API + '/signup', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });
                const data = await res.json();
                if (data.success) {
                    toast('Signup successful, please login');
                    show('login');
                } else {
                    toast(data.msg || 'Signup failed');
                }
            } catch (e) {
                toast('Network error. Please try again.');
            }
        }

        /* ======= Chat ======= */
        const chatEl = document.getElementById('chat');
        function addBubble(text, who) {
            const div = document.createElement('div');
            div.className = 'bubble ' + (who === 'me' ? 'me' : 'ai');
            div.textContent = text;
            chatEl.appendChild(div);
            chatEl.scrollTop = chatEl.scrollHeight;
        }

        async function send() {
            const input = document.getElementById('command');
            const cmd = input.value.trim();
            if (!cmd) return;
            addBubble(cmd, 'me');
            input.value = '';
            try {
                const res = await fetch(API + '/command', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ command: cmd })
                });
                const data = await res.json();
                addBubble(data.response || '...', 'ai');
                // optional: speak on client too
                if ('speechSynthesis' in window && data.response) {
                    speechSynthesis.speak(new SpeechSynthesisUtterance(data.response));
                }
            } catch (e) {
                addBubble('⚠ Cannot reach server', 'ai');
            }
        }
        function newChat() { chatEl.innerHTML = ''; }

        /* ======= History ======= */
        async function openHistory() {
            try {
                const res = await fetch(API + '/history');
                const list = await res.json(); // backend returns a LIST directly
                const container = document.getElementById('history');
                container.innerHTML = '';
                [...list].reverse().forEach(h => {
                    const d = document.createElement('div');
                    d.className = 'hist-item';
                    d.innerHTML = `<b>${h.time}</b><br><i>You:</i> ${h.command}<br><i>Swastik:</i> ${h.response}`;
                    container.appendChild(d);
                });

                // also show modal view
                const sheet = document.getElementById('historySheet');
                sheet.innerHTML = container.innerHTML;
                document.getElementById('historyModal').style.display = 'flex';
            } catch (e) {
                toast('Failed to load history');
            }
        }
        function hideModal() { document.getElementById('historyModal').style.display = 'none'; }
        function closeModal(e) { if (e.target.id === 'historyModal') hideModal(); }

        /* ======= Voice Input 🎤 (Web Speech API) ======= */
        const recLabel = document.getElementById('recState');
        const micBtn = document.getElementById('micBtn');
        let recognition = null;
        let recActive = false;

        function setupRecognizer() {
            const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SR) return null;
            const r = new SR();
            r.lang = 'en-US';
            r.interimResults = false;
            r.maxAlternatives = 1;
            r.continuous = false;
            r.onstart = () => {
                recLabel.textContent = 'Listening…';
                micBtn.classList.add('recording');
                recActive = true;
            };
            r.onend = () => {
                recLabel.textContent = 'Idle';
                micBtn.classList.remove('recording');
                recActive = false;
            };
            r.onerror = (e) => {
                recLabel.textContent = 'Mic error';
                console.warn(e);
                recActive = false;
                micBtn.classList.remove('recording');
            };
            r.onresult = (ev) => {
                const text = ev.results[0][0].transcript;
                const input = document.getElementById('command');
                input.value = text;
                send();
            };
            return r;
        }

        function toggleMic() {
            if (!recognition) { recognition = setupRecognizer(); }
            if (!recognition) { toast('Speech Recognition not supported in this browser.'); return; }
            if (recActive) { recognition.stop(); recActive = false; }
            else { recognition.start(); recActive = true; }
        }

        /* ======= Enter to Send ======= */
        document.getElementById('command').addEventListener('keydown', (e) => {
            if (e.key === 'Enter') send();
        });
