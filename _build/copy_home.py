"""Homepage copy from content/homepage.md v3 (via the approved board's copy_text.py) (Oct 16, revised around Ben's brand thesis).
Verbatim except the edits marked EDIT, which move the mockup names into the real shots' world
(Nora Castillo / Fernhill Studio): Priya Raman -> Ava Lindqvist (Saltmarsh Coffee, Portland, Maine, Eastern time),
Lachlan -> Marco Reyes (Tidewater Print), Tidewater onsite -> Saltmarsh shoot walkthrough.
Oct 17: the positioning review's quick wins (content/positioning-review-2026-10.md §5), the new Split-view section (R2),
People moved to third and rewritten (R3), two new FAQs (R7). content/homepage.md mirrors this file."""

HERO_H = 'Mail that knows what needs you.'
HERO_NOTE = 'Give your inbox some margin.'
HERO_SUB = ('A native Mac email app for Gmail, with your calendar and the people you work with in one window. '
            'MarginMail finds time in your day, keeps what matters and marks what needs you, privately.')  # v3
PRIV_LINE = 'Just your email. No tracking.'
SMALL_LINE = 'Free during the beta · macOS 26 or later · Gmail and Google Workspace'  # v3

WHAT_IS = dict(lbl='What is MarginMail?',  # v3, new block after the hero (id="how")
    lead='MarginMail is a native Mac email app for Gmail and Google Workspace, with a calendar and a personal CRM built in.',
    rest=(' It notes what needs you (follow-ups, meeting invites and requests), helps you find a meeting time as you type, and gives '
          'everyone you write to a page. Its AI is optional: Apple Intelligence on your Mac, or your own Claude when you click, never a MarginMail server, '
          'and it never sends email for you.'))

MANIFESTO = dict(
    lbl='What the margin is for',
    text=('The margin is where the work gets clear. Every good page of notes has one. It’s where you find time in a full day. '
          'Where you keep the facts worth remembering. Where you skim to see what was decided and what still needs you. '
          'Where you underline what matters, circle the ask, and make the call. MarginMail brings that to your mail. It finds the '
          'time, keeps your people close, marks what needs you, and turns a chaotic day into a short, ordered stack. '
          'Then it gets out of the way.'),
    note='this is the whole idea',
    # (mark, title, line, features, note)
    cards=[
        ('circle', 'Find time', 'Type “Tuesday with Ava” and both calendars’ free times appear.',              # EDIT name
         'Find a time · Live words · Calendar built in', 'found 30 minutes'),
        ('star', 'Keep what matters', 'Everyone you write to has a page: what you promised, what they’re waiting on, and the time where they are.',  # Oct 17, R8
         'People pages · Companies · Notes', 'remember: she’s on Eastern time'),                                 # EDIT (Ava is in Maine)
        ('underline', 'Skim, then know', 'See why something’s here, what’s been decided, and the exact sentence that asks.',
         '“Why this?” · What’s been decided · Highlighted asks', 'decided: ship Thursday'),
        ('arrow', 'Make the call', 'What needs you is a stack. Right for Done, left for Later, or reply.',
         'The Margins stack · Done · Later · Write it', 'Done. Next.'),
        ('bracket', 'Bring order', 'A messy day becomes a short stack, and an empty one ends in a sunrise.',
         'The Margins stack · All clear scenes', 'from 35 to 5'),
        ('highlight', 'Mark what matters', 'MarginMail highlights the ask in the message and marks the row in the margin.',
         'Highlighted ask · The margin mark', 'this is the ask'),
    ])

S_STACK = dict(lbl='Follow-up reminders, requests and meeting invites', h='Only what needs you.',
          body=("MarginMail writes a short note in the margin when someone's waiting on you, when you're waiting on a reply, "
                "or when a meeting invite needs an answer. Open the stack and work through them like cards: drag right for Done, left for Later."),
          chips=[('Follow-ups', '“You asked Ava on Oct 9. No reply in 6 days.”'),                     # EDIT name
                 ('Meetings', '“Unanswered invite: Saltmarsh shoot walkthrough, Thursday.”'),          # EDIT name
                 ('Requests', '“Marco asked for the signed proof by Thursday.”')],                    # EDIT name + item (matches the shot)
          below='Every card has a <b>Why this?</b> that shows exactly what MarginMail noticed. Cards flip over to show their email.',
          note='right for Done')

# Oct 17, R2: the one-window story, second after the stack. Names match the Split-view render (Imogen Hale, Kiln & Co.).
S_SPLIT = dict(lbl='Email, calendar and contacts in one Mac window', h='Your mail, your calendar and your people, side by side.',
          body=('Open Split view and your whole day is in one window. Read Imogen’s message, and her page is a click away: what you '
                'last talked about and the time where she is. Today’s calendar sits beside it. An invite you haven’t answered looks '
                'different. Press A, M or D, and its email files itself. No tab to keep open, no app to switch to.'),
          note='no tab to keep open')

S_TIME = dict(lbl='Google Calendar built in, with Find a time', h='Find time in the margins of your day.',
          body=('The full calendar is one click away. Meeting invites you haven’t answered look different, and a '
                '<b>Needs your answer</b> list keeps them together, each answered with one key. Need to schedule a meeting? '
                'See both calendars side by side, pick a time, and the hold is placed for you.'),
          note='there’s your hour')

S_LIVE = dict(lbl='Schedule meetings and attach files as you type', h='Type the plan. MarginMail does the rest.',
          body=('As you write, dates, people, files and promises become actions. Type “Tuesday with Ava” and both calendars’ '
                'free times appear. Type “the pricing deck” and the file is attached. It’s all rules, so it’s instant, private and works with AI off.'),   # EDIT name
          sample=('Tuesday with Ava', ' works, I’ll send the pricing deck by Friday.'),                            # EDIT name (the shot's sentence)
          note='just type it')

S_SKIM = dict(lbl='Email summaries and highlighted asks', h='Skim it. Know what matters.',
          body=('When someone asks you for something, MarginMail highlights the exact sentence and marks the row in the margin. '
                'Every card says why it’s there. On a long thread, <b>What’s been decided</b> sums it up: what’s settled, what’s still '
                'open and who’s waiting on whom.'),
          note='this is the ask')

S_WRITE = dict(lbl='Private AI email replies you send yourself', h='A draft from your notes. Sent by you.',  # Oct 17, O1
          body=('Jot a few notes and press <b>Write it</b>. MarginMail drafts the reply from your notes and the thread, right in front of you, '
                'and flags anything it added that the thread didn’t have. You read it. You send it.'),
          priv=('Write it uses your own Claude, signed in on this Mac, only when you click. Only that conversation goes to Anthropic, '
                'under your plan. Request notes use Apple Intelligence, on-device. MarginMail works fully with AI off.'),  # Oct 17, O2
          note='new: check this')

S_PEOPLE = dict(lbl='A private personal CRM, built from your Gmail and calendar', h='Everyone you write to has a page.',  # Oct 17, R3
          body=('Before a meeting, open their page: what you last talked about, what you promised, who’s waiting on whom, and the '
                'time where they are. Tasks close themselves when the reply, the file or the yes arrives. Companies group themselves '
                'by email domain. It’s all built from the mail and calendar you already have, and it stays in your own Google account. '
                'Nothing to import. Nothing uploaded.'),
          note='remember: she’s on Eastern time')                                                      # EDIT (was: she's in London)

DETAILS = dict(lbl='The details',
          items=[('In-window composer.', 'Docked, floating anywhere or expanded over the reader. Your inbox never disappears.'),
                 ('Done, not Archive.', 'Handled mail leaves. That’s the whole idea.'),
                 ('Multiple Gmail accounts.', 'Several Google accounts, one unified inbox. Plus Dock badge, signatures and View › Zoom.'),
                 ('Your day in the menu bar.', 'Today’s agenda one click away, with Join for the next call.'),            # Oct 17, R6
                 ('Notifications for what needs you.', 'Per account: everything, only what needs you and your VIPs, or nothing. Quiet hours and Focus filters too.')])

# Speed & craft + Privacy promise merged (Ben, Oct 16: "Made for the Mac, made for privacy"; no engineering stats)
S_MACPRIV = dict(lbl='Private email: no servers, no tracking', h='Made for the Mac. Made for privacy.',
          body=('MarginMail is a native Mac app, built from the start to keep your mail yours. There’s no MarginMail server in the '
                'middle: we can’t read your mail, and we can’t see how you use the app.'),
          points=[('No usage tracking.', 'No analytics or telemetry in the app, so we can’t see how you use it. This site sets no cookies and doesn’t track you: we count visits anonymously on our own server, with no ads or third parties, and we honor Do Not Track.'),
                  ('Tracking pixels blocked.', 'Remote images are blocked by default. Load them for one message, or always for a sender you trust. Hidden 1×1 tracking pixels are stripped even when you load images, and the images MarginMail does load are fetched without cookies or referrer.'),
                  ('No read receipts.', 'MarginMail never adds read receipts or open tracking to the mail you send.'),
                  ('No MarginMail server.', 'Your mail goes between your Mac and Google, and nowhere else.'),
                  ('AI that stays with you.', 'Apple Intelligence on your Mac first. Your own Claude only if you opt in, and only when you click. AI never sends.'),  # Oct 17, R8
                  ('Your data, your account.', 'MarginMail’s own data lives in your Google account’s private app folder.')],
          note='pixels stay out')

S_JOY = dict(lbl='Inbox zero, with a sunrise', h='Done feels good here.',
          body=('Clear the stack and MarginMail shows a calm scene for a moment: a sunrise over the horizon, still water, a beam '
                'of light, chosen by the time of day. Small things like that are on purpose.'),
          note='all clear, see?')

CTA = dict(h='Come try it early.',
           body='MarginMail is in beta for Mac with Gmail and Google Workspace accounts. We’re letting people in a few at a time so we can listen closely.')

FAQ = [  # v3: 14 questions as people ask them (follow-up example uses Ava, EDIT name); Oct 17: 16, with R7's two and O4/O5
 ('What is MarginMail?', 'MarginMail is a native Mac email app for Gmail and Google Workspace, with a calendar and a personal CRM built in. It notes what needs you, helps you find meeting times as you type, and gives everyone you write to a page. Its optional AI uses Apple Intelligence on your Mac or your own Claude, and never sends email.'),
 ('Is there a native Gmail app for Mac?', 'Google doesn’t make a Gmail app for the Mac; Gmail runs in a browser. MarginMail is a native macOS app built on the Gmail API, so your Gmail and Google Workspace accounts get real Mac windows, notifications and keyboard shortcuts, with your calendar and the people you write to in the same window.'),
 ('Does MarginMail store my emails on its servers?', 'No. There is no MarginMail server for your mail. MarginMail connects directly to Google from your Mac, so your messages stay with you and Google. MarginMail’s own small settings live in your Google Drive’s hidden app folder. There are no analytics in the app, so we can’t see how you use it.'),
 ('Does MarginMail have a built-in personal CRM?', 'Yes. Everyone you write to gets a page built from your mail and calendar: past conversations, meetings, notes, tasks and their local time, grouped by company. Tasks close themselves when the reply or file arrives. It stays in your own Google account. Nothing is uploaded to a CRM service, and there’s nothing to import.'),
 ('Is MarginMail’s AI private?', 'Yes. Request notes use Apple Intelligence on your Mac, so nothing leaves it. If you choose, Write it and What’s been decided use your own Claude, signed in on your Mac, only when you click. Only that one conversation goes to Anthropic, under your own plan. MarginMail never sees your Claude login, uses no API key, and runs no AI server.'),
 ('Can I use MarginMail without AI?', 'Yes. MarginMail works fully with AI off. Follow-up and meeting notes, live words, the calendar, Find a time, People and Companies all run on plain rules. Turning AI on adds Request notes, which are found on your Mac, and Write it, which drafts replies with your own Claude.'),
 ('Can MarginMail’s AI send emails for me?', 'No, never. MarginMail’s AI can draft a reply, but only you can send it. Before you do, MarginMail flags anything the draft added that the thread didn’t have, such as a new recipient, a link, a number or a code, and labels which AI wrote it.'),
 ('Does MarginMail work with multiple Gmail accounts?', 'Yes. You can add several Gmail and Google Workspace accounts and see them in one unified inbox, with your calendars together beside it. MarginMail supports Google accounts today. iCloud and other providers are planned for later, and MarginMail will say so clearly when they arrive.'),
 ('Does MarginMail have a calendar?', 'Yes. Your Google Calendar sits beside your inbox. Invitations you haven’t answered look different and gather in a Needs your answer list. Press A, M or D to accept, maybe or decline, and the invite’s email files itself. Find a time shows both calendars side by side when Google shares theirs with you, and places the hold.'),
 ('Can I see my email and calendar in one window on Mac?', 'Yes. MarginMail’s Split view shows your inbox, the message and today’s calendar side by side. Click a name to see that person’s page. Answer invites with A, M or D, and their email files itself. It works with several Google accounts and calendars at once.'),
 ('How do follow-up reminders work in MarginMail?', 'When you’re waiting on a reply, MarginMail notices and writes a note in the reply bar, like “You asked Ava on Oct 9. No reply in 6 days.” The note joins your Margins stack so you can nudge, mark it Done or move it to Later. It works on rules, with AI off.'),
 ('Does MarginMail use read receipts or tracking pixels?', 'No. MarginMail never adds read receipts or open tracking to the mail you send. It also blocks remote images in mail you receive by default, so senders’ tracking pixels don’t load unless you allow images for that sender.'),
 ('How much does MarginMail cost?', 'MarginMail is free during the beta. Pricing will be announced before the beta ends, well before anything changes for you. Joining the beta only needs your email address, and the only email we’ll send is your invite.'),
 ('Is there a MarginMail app for iPhone?', 'Not yet. MarginMail starts on the Mac, where your mail, calendar and people share one window. An iPhone companion app is planned for later. Until then, your mail stays in Gmail as usual, so you can keep using Gmail on your phone.'),
 ('Is MarginMail the same as the Margin app for iPhone?', 'No. MarginMail is our own Apple-native email app for the Mac, built for Gmail and Google Workspace, with an iPhone companion app planned for later. It isn’t affiliated with other apps named Margin. Everything about MarginMail is on marginmail.ai, and the beta is free to join.'),
 ('What Mac do I need for MarginMail?', 'MarginMail needs macOS 26 or later. Request notes use Apple Intelligence, so they need a Mac where Apple Intelligence is available and turned on. Everything else, including the calendar, follow-up notes, live words and People, works without it.'),
 ('When can I join the MarginMail beta?', 'Join the list on this page and we’ll email you when your invite is ready. We’re letting people in a few at a time so we can listen closely to each wave. Your email address is all we ask for. This site sets no cookies and doesn’t track you; we only count visits anonymously on our own server.'),
]

FOOT_LINE = 'Mail that knows what needs you. A native Mac email app for Gmail.'  # v3
FOOT_LINKS = ['Compare MarginMail', 'Answers', 'Privacy', 'Terms', 'Contact']  # v3
FOOT_SMALL = 'Made with love for the Mac. No cookies, no tracking. We count visits anonymously on our own server — no ads, no third parties, and we honor Do Not Track. · © 2026 MarginMail'
