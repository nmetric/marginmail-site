"""Homepage copy from content/homepage.md v3 (via the approved board's copy_text.py) (Oct 16, revised around Ben's brand thesis).
Verbatim except the edits marked EDIT, which move the mockup names into the real shots' world
(Nora Castillo / Fernhill Studio): Priya Raman -> Ava Lindqvist (Saltmarsh Coffee, Portland, Maine, Eastern time),
Lachlan -> Marco Reyes (Tidewater Print), Tidewater onsite -> Saltmarsh shoot walkthrough."""

HERO_H = 'Mail that knows what needs you.'
HERO_NOTE = 'Give your inbox some margin.'
HERO_SUB = ('A native Mac email app for Gmail, with your calendar and the people you work with in one window. '
            'Margin finds time in your day, keeps what matters and marks what needs you, privately.')  # v3
PRIV_LINE = 'Just your email. No tracking.'
SMALL_LINE = 'Free during the beta · macOS 26 or later · Gmail and Google Workspace'  # v3

WHAT_IS = dict(lbl='What is Margin?',  # v3, new block after the hero (id="how")
    lead='Margin is a native Mac email app for Gmail and Google Workspace, with a calendar and a personal CRM built in.',
    rest=(' It notes what needs you (follow-ups, meeting invites and requests), helps you find a meeting time as you type, and gives '
          'everyone you write to a page. Its AI is optional: it runs on your Mac or through your own Claude, never on a Margin server, '
          'and it never sends email for you.'))

MANIFESTO = dict(
    lbl='What the margin is for',
    text=('The margin is where the work gets clear. Every good page of notes has one. It’s where you find time in a full day. '
          'Where you keep the facts worth remembering. Where you skim to see what was decided and what still needs you. '
          'Where you underline what matters, circle the ask, and make the call. Margin brings that to your mail. It finds the '
          'time, keeps your people close, marks what needs you, and turns a chaotic day into a short, ordered stack. '
          'Then it gets out of the way.'),
    note='this is the whole idea',
    # (mark, title, line, features, note)
    cards=[
        ('circle', 'Find time', 'Type “Tuesday with Ava” and both calendars’ free times appear.',              # EDIT name
         'Find a time · Live words · Calendar built in', 'found 30 minutes'),
        ('star', 'Keep what matters', 'Everyone you write to has a page, with your notes and their local time.',
         'People pages · Companies · Notes', 'remember: she’s on Eastern time'),                                 # EDIT (Ava is in Maine)
        ('underline', 'Skim, then know', 'See why something’s here, what’s been decided, and the exact sentence that asks.',
         '“Why this?” · What’s been decided · Highlighted asks', 'decided: ship Thursday'),
        ('arrow', 'Make the call', 'What needs you is a stack. Right for Done, left for Later, or reply.',
         'The Margins stack · Done · Later · Write it', 'Done. Next.'),
        ('bracket', 'Bring order', 'A messy day becomes a short stack, and an empty one ends in a sunrise.',
         'The Margins stack · All clear scenes', 'from 35 to 5'),
        ('highlight', 'Mark what matters', 'Margin highlights the ask in the message and marks the row in the margin.',
         'Highlighted ask · The margin mark', 'this is the ask'),
    ])

S_STACK = dict(lbl='Follow-up reminders, requests and meeting invites', h='Only what needs you.',
          body=("Margin writes a short note in the margin when someone's waiting on you, when you're waiting on a reply, "
                "or when a meeting invite needs an answer. Open the stack and work through them like cards: drag right for Done, left for Later."),
          chips=[('Follow-ups', '“You asked Ava on Oct 9. No reply in 6 days.”'),                     # EDIT name
                 ('Meetings', '“Unanswered invite: Saltmarsh shoot walkthrough, Thursday.”'),          # EDIT name
                 ('Requests', '“Marco asked for the signed proof by Thursday.”')],                    # EDIT name + item (matches the shot)
          below='Every card has a <b>Why this?</b> that shows exactly what Margin noticed. Cards flip over to show their email.',
          note='right for Done')

S_TIME = dict(lbl='Email and calendar in one window', h='Find time in the margins of your day.',
          body=('Your calendar sits right beside your inbox. Meeting invites you haven’t answered look different, and a '
                '<b>Needs your answer</b> list keeps them together. Accept with A, Maybe with M, Decline with D, and the email '
                'files itself. Need to schedule a meeting? See both calendars side by side, pick a time, and the hold is placed for you.'),
          note='there’s your hour')

S_LIVE = dict(lbl='Schedule meetings and attach files as you type', h='Type the plan. Margin does the rest.',
          body=('As you write, dates, people, files and promises become actions. Type “Tuesday with Ava” and both calendars’ '
                'free times appear. Type “the pricing deck” and the file is attached. It’s all rules, so it’s instant, private and works with AI off.'),   # EDIT name
          sample=('Tuesday with Ava', ' works, I’ll send the pricing deck by Friday.'),                            # EDIT name (the shot's sentence)
          note='just type it')

S_SKIM = dict(lbl='Email summaries and highlighted asks', h='Skim it. Know what matters.',
          body=('When someone asks you for something, Margin highlights the exact sentence and marks the row in the margin. '
                'Every card says why it’s there. On a long thread, <b>What’s been decided</b> sums it up: what’s settled, what’s still '
                'open and who’s waiting on whom.'),
          note='this is the ask')

S_WRITE = dict(lbl='Private AI email replies, written in your voice', h='A draft in your voice. Sent by you.',
          body=('Jot a few notes and press <b>Write it</b>. Margin drafts the reply in your voice, right in front of you, '
                'and flags anything it added that the thread didn’t have. You read it. You send it.'),
          priv=('Write it uses your own Claude on this Mac, only if you turn it on. Request notes use Apple Intelligence, '
                'on-device. Margin works fully with AI off.'),
          note='new: check this')

S_PEOPLE = dict(lbl='A personal CRM built from your email and calendar', h='Everyone you write to has a page.',
          body=('Conversations, meetings, tasks and their local time, all in one place, built from the mail and calendar you '
                'already have. Companies group themselves by email domain, and breadcrumbs always lead you back to where you were.'),
          note='remember: she’s on Eastern time')                                                      # EDIT (was: she's in London)

DETAILS = dict(lbl='The details',
          items=[('In-window composer.', 'Docked, floating anywhere or expanded over the reader. Your inbox never disappears.'),
                 ('Done, not Archive.', 'Handled mail leaves. That’s the whole idea.'),
                 ('Multiple Gmail accounts.', 'Several Google accounts in one unified inbox, plus Dock badge, notifications, signatures and View › Zoom.')])  # v3

# Speed & craft + Privacy promise merged (Ben, Oct 16: "Made for the Mac, made for privacy"; no engineering stats)
S_MACPRIV = dict(lbl='Private email: no servers, no tracking', h='Made for the Mac. Made for privacy.',
          body=('Margin is a native Mac app, built from the start to keep your mail yours. There’s no Margin server in the '
                'middle: we can’t read your mail, and we can’t see how you use the app.'),
          points=[('No usage tracking.', 'No analytics or telemetry in the app, so we can’t see how you use it. This site sets no cookies and doesn’t track you: we count visits anonymously on our own server, with no ads or third parties, and we honor Do Not Track.'),
                  ('Tracking pixels blocked.', 'Remote images are blocked by default. Load them for one message, or always for a sender you trust. Hidden 1×1 tracking pixels are stripped even when you load images, and the images Margin does load are fetched without cookies or referrer.'),
                  ('No read receipts.', 'Margin never adds read receipts or open tracking to the mail you send.'),
                  ('No Margin server.', 'Your mail goes between your Mac and Google, and nowhere else.'),
                  ('AI that stays with you.', 'Apple Intelligence on your Mac first; your own Claude only if you opt in. AI never sends.'),
                  ('Your data, your account.', 'Margin’s own data lives in your Google account’s private app folder.')],
          note='pixels stay out')

S_JOY = dict(lbl='Inbox zero, with a sunrise', h='Done feels good here.',
          body=('Clear the stack and Margin shows a calm scene for a moment: a sunrise over the horizon, still water, a beam '
                'of light, chosen by the time of day. Small things like that are on purpose.'),
          note='all clear, see?')

CTA = dict(h='Come try it early.',
           body='Margin is in beta for Mac with Gmail and Google Workspace accounts. We’re letting people in a few at a time so we can listen closely.')

FAQ = [  # v3: 14 questions as people ask them (follow-up example uses Ava, EDIT name)
 ('What is Margin?', 'Margin is a native Mac email app for Gmail and Google Workspace, with a calendar and a personal CRM built in. It notes what needs you, helps you find meeting times as you type, and gives everyone you write to a page. Its optional AI runs on your Mac and never sends email.'),
 ('Is there a native Gmail app for Mac?', 'Google doesn’t make a Gmail app for the Mac; Gmail runs in a browser. Margin is a native macOS app built on the Gmail API, so your Gmail and Google Workspace accounts get real Mac windows, notifications and keyboard shortcuts, with your calendar and the people you write to in the same window.'),
 ('Does Margin store my emails on its servers?', 'No. There is no Margin server for your mail. Margin connects directly to Google from your Mac, so your messages stay with you and Google. Margin’s own small settings live in your Google Drive’s hidden app folder. There are no analytics in the app, so we can’t see how you use it.'),
 ('Is Margin’s AI private?', 'Yes. Request notes use Apple Intelligence on your Mac, so nothing leaves it. If you choose, Write it and What’s been decided use your own Claude on your Mac, under your own plan, only when you click. Margin never sees your Claude login, uses no API key, and runs no AI server.'),
 ('Can I use Margin without AI?', 'Yes. Margin works fully with AI off. Follow-up and meeting notes, live words, the calendar, Find a time, People and Companies all run on plain rules. Turning AI on adds Request notes, which are found on your Mac, and Write it, which drafts replies with your own Claude.'),
 ('Can Margin’s AI send emails for me?', 'No, never. Margin’s AI can draft a reply, but only you can send it. Before you do, Margin flags anything the draft added that the thread didn’t have, such as a new recipient, a link, a number or a code, and labels which AI wrote it.'),
 ('Does Margin work with multiple Gmail accounts?', 'Yes. You can add several Gmail and Google Workspace accounts and see them in one unified inbox, with your calendars together beside it. Margin supports Google accounts today. iCloud and other providers are planned for later, and Margin will say so clearly when they arrive.'),
 ('Does Margin have a calendar?', 'Yes. Your Google Calendar sits beside your inbox. Invitations you haven’t answered look different and gather in a Needs your answer list. Press A, M or D to accept, maybe or decline, and the invite’s email files itself. Find a time shows both calendars side by side and places the hold.'),
 ('How do follow-up reminders work in Margin?', 'When you’re waiting on a reply, Margin notices and writes a note in the reply bar, like “You asked Ava on Oct 9. No reply in 6 days.” The note joins your Margins stack so you can nudge, mark it Done or move it to Later. It works on rules, with AI off.'),
 ('Does Margin use read receipts or tracking pixels?', 'No. Margin never adds read receipts or open tracking to the mail you send. It also blocks remote images in mail you receive by default, so senders’ tracking pixels don’t load unless you allow images for that sender.'),
 ('How much does Margin cost?', 'Margin is free during the beta. Pricing will be announced before the beta ends, well before anything changes for you. Joining the beta only needs your email address, and the only email we’ll send is your invite.'),
 ('Is there a Margin app for iPhone?', 'Not yet. Margin starts on the Mac, where your mail, calendar and people share one window. An iPhone companion app is planned for later. Until then, your mail stays in Gmail as usual, so you can keep using Gmail on your phone.'),
 ('What Mac do I need for Margin?', 'Margin needs macOS 26 or later. Request notes use Apple Intelligence, so they need a Mac where Apple Intelligence is available and turned on. Everything else, including the calendar, follow-up notes, live words and People, works without it.'),
 ('When can I join the Margin beta?', 'Join the list on this page and we’ll email you when your invite is ready. We’re letting people in a few at a time so we can listen closely to each wave. Your email address is all we ask for. This site sets no cookies and doesn’t track you; we only count visits anonymously on our own server.'),
]

FOOT_LINE = 'Mail that knows what needs you. A native Mac email app for Gmail.'  # v3
FOOT_LINKS = ['Compare Margin', 'Answers', 'Privacy', 'Terms', 'Contact']  # v3
FOOT_SMALL = 'Made on a Mac by Ben Nowacky. No cookies, no tracking. We count visits anonymously on our own server — no ads, no third parties, and we honor Do Not Track. · © 2026 Margin'
