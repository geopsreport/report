import re

class Analyst:
    def __init__(self, name, websites, description):
        self.name = name
        self.websites = websites
        self.description = description

    @property
    def analyst_id(self):
        # Deterministically generate an ID from the name (lowercase, dashes, no punctuation)
        id_ = self.name.lower()
        id_ = re.sub(r'[^a-z0-9]+', '-', id_)
        id_ = id_.strip('-')
        return id_

    @property
    def filename(self):
        return self.analyst_id + '.md'

    def analyst_url(self, baseurl=""):
        return f"{baseurl}/analysts/{self.analyst_id}"
    
    @staticmethod
    def find_analyst(name):
        for a in analysts:
            if a.get("name") == name:
                return Analyst(a.get("name"), a.get("websites"), a.get("description"))
        return None

analysts = [
    {
        "name": "Larry C. Johnson",
        "websites": ["https://sonar21.com"],
        "description": "Former CIA analyst & State Dept counterterrorism official; runs Sonar21 blog covering national security and global affairs from a skeptical, realist viewpoint."
    },
    {
        "name": "Daniel L. Davis",
        "websites": ["https://19fortyfive.com"],
        "description": "Retired US Army Lt. Colonel and defense fellow; contributes critical analysis on US military strategy, especially regarding Ukraine and budget."
    },
    {
        "name": "Ray McGovern",
        "websites": ["https://consortiumnews.com"],
        "description": "27-year CIA analyst turned independent; co-founder of Veteran Intelligence Professionals for Sanity; writes critical open-source intel assessments."
    },
    {
        "name": "Philip Giraldi",
        "websites": ["https://www.unz.com/author/philip-giraldi/"],
        "description": "Former CIA case/military intel officer; now security consultant and columnist; directs Council for the National Interest; anti-interventionist realism."
    },
    {
        "name": "Andrei Martyanov",
        "websites": ["https://smoothiex12.blogspot.com/"],
        "description": "Former Soviet naval officer and military analyst; runs 'Reminiscence of the Future' blog, focusing on Russian vs US military-industrial realities."
    },
    {
        "name": "Chas W. Freeman Jr.",
        "websites": ["https://chasfreeman.net"],
        "description": "Retired US diplomat and China/Middle East expert; realist voice on geopolitics; archives speeches/articles critical of US policy."
    },
    {
        "name": "Alastair Crooke",
        "websites": ["https://www.eurasiareview.com/author/alastair-crooke/"],
        "description": "Ex-MI6 diplomat and founder of Conflicts Forum (Beirut); publishes deep Middle East and great-power essays independent of Western institutional frames."
    },
    {
        "name": "Patrick Armstrong",
        "websites": ["https://patrickarmstrong.ca/"],
        "description": "Former Canadian diplomat in Moscow; independent analyst of Russia–West relations with realist, multipolar perspective."
    },
    {
        "name": "M. K. Bhadrakumar",
        "websites": ["https://indianpunchline.com"],
        "description": "Retired Indian ambassador with deep Eurasia/Middle East experience; publishes sharp Global South realist commentary."
    },
    {
        "name": "Alex Krainer",
        "websites": ["https://alexkrainer.substack.com"],
        "description": "Independent market & geopolitical analyst (Croatian background); author of The Naked Hedgie Substack, critical of mainstream financial-media narratives."
    },
    {
        "name": "Glenn Diesen",
        "websites": ["https://glenndiesen.substack.com"],
        "description": "Norwegian political scientist, pro-multipolar realism; focuses on Russia, geoeconomics and critiques Western-led order."
    },
    {
        "name": "Mark Sleboda",
        "websites": ["https://marksleboda.substack.com"],
        "description": "US Navy vet based in Moscow; hosts 'The Real Politick'; realist analysis of Russia–US tensions, often dismantling Western narratives."
    },
    {
        "name": "Chris Hedges",
        "websites": ["https://scheerpost.com"],
        "description": "Pulitzer-winning journalist, ex–NYT war correspondent; radical realist and moral critique of empire; writes weekly and hosts Substack."
    },
    {
        "name": "Pepe Escobar",
        "websites": ["https://pepeescobar.substack.com"],
        "description": "Brazilian Eurasia-focused journalist; covers multipolar world, China, BRICS; independent reporting blending on-the-ground insights."
    },
    {
        "name": "Patrick Lawrence",
        "websites": ["https://thefloutist.substack.com"],
        "description": "Veteran foreign–affairs journalist; first to contest Russiagate; writes longform critique of US media, war policy, and establishment narratives."
    },
    {
        "name": "Caitlin Johnstone",
        "websites": ["https://www.caitlinjohnst.one/"],
        "description": "Australian satirical anti–war journalist; reader–funded Substack; challenges media propaganda and US/NATO interventions daily."
    },
    {
        "name": "Thierry Meyssan",
        "websites": ["https://voltairenet.org"],
        "description": "French activist-journalist; founder of Voltaire Network; writes in French/English challenging Western media on war, disinformation, geopolitics."
    },
    {
        "name": "Elijah J. Magnier",
        "websites": ["https://ejmagnier.com"],
        "description": "Veteran Middle East war correspondent; provides first-hand analysis of Syria, Iraq, Gaza; writes for The Cradle and personal blog."
    },
    {
        "name": "Jan Oberg",
        "websites": ["https://transnational.live/"],
        "description": "Swedish peace researcher and co–founder of Transnational Foundation; independent thought leadership on conflict resolution and non–violence."
    },
    {
        "name": "Moon of Alabama (Bernhard)",
        "websites": ["https://moonofalabama.org"],
        "description": "Anonymous German blogger; daily open–source intelligence deep–dives, critical of NATO/Western media, widely followed by OSINT community."
    },
    {
        "name": "Boris Rozhin (Colonel Cassad)",
        "websites": ["https://colonelcassad.livejournal.com/"],
        "description": "Russian military-history analyst; Crimea–based; provides minute–by–minute OSINT on Ukraine from pro–resistance, anti–NATO viewpoint."
    },
    {
        "name": "Jeffrey Sachs",
        "websites": ["https://www.commondreams.org/author/jeffrey-d-sachs"],
        "description": "Columbia economist and former UN advisor; writes on global development, sustainable multipolarity; frequently published via Project Syndicate & Consortium News."
    },
    {
        "name": "Glenn Greenwald",
        "websites": ["https://greenwald.substack.com"],
        "description": "Pulitzer-winner, ex–Intercept co–founder; focuses on surveillance, civil liberties, media critique and relentless foreign–policy skepticism."
    },
    {
        "name": "Max Blumenthal",
        "websites": ["https://thegrayzone.com"],
        "description": "Investigative journalist and filmmaker; founder of The Grayzone; covers Middle East, media bias, imperialism and regime-change narratives."
    },
    {
        "name": "John Pilger",
        "websites": ["https://consortiumnews.com"],
        "description": "Veteran Australian journalist and filmmaker; writes long-form critiques of Western foreign policy via personal site and Consortium News."
    },
    {
        "name": "Binoy Kampmark",
        "websites": ["https://counterpunch.org/author/jete6/"],
        "description": "Cambridge–educated researcher at RMIT; writes widely on imperialism, international law, Australia's role; publishes at CounterPunch, ZNetwork, The Mandarin."
    },
    {
        "name": "Rana Abou Rjeily",
        "websites": ["https://ranahabib.substack.com"],
        "description": "Lebanese writer and typographer based in Beirut; Substack offers cultural/political reflections from Middle East intersectional angle."
    },
    {
        "name": "Nicolai N. Petro",
        "websites": [
            "https://www.npetro.net/8.html",
            "https://www.npetro.net/7.html",
            "https://www.npetro.net/4.html"
        ],
        "description": "Nicolai N. Petro is a Professor of Political Science specializing in Russian and Eurasian politics, known for his critical analysis of East-West relations and advocacy for diplomatic engagement."
    },
    {
        "name": "Richard Falk",
        "websites": [
            "https://richardfalk.org/"
        ],
        "description": "Richard Falk is an international law and international relations scholar who taught at Princeton University for forty years. Since 2002 he has lived in Santa Barbara, California, and taught at the local campus of the University of California in Global and International Studies and since 2005 chaired the Board of the Nuclear Age Peace Foundation. He initiated this blog partly in celebration of his 80th birthday."
    }
]

def get_analyst_objects():
    return [Analyst(a["name"], a["websites"], a["description"]) for a in analysts]
