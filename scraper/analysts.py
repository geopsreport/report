import re

class Analyst:
    def __init__(self, name, website, description):
        self.name = name
        self.website = website
        self.description = description

    @property
    def analyst_id(self):
        # Deterministically generate an ID from the name (lowercase, dashes, no punctuation)
        id_ = self.name.lower()
        id_ = re.sub(r'[^a-z0-9]+', '-', id_)
        id_ = id_.strip('-')
        return id_

    def analyst_url(self, baseurl=""):
        return f"{baseurl}/analyst/{self.analyst_id}/"
    
    @staticmethod
    def find_analyst(name):
        for a in analysts:
            if a.get("name") == name:
                return Analyst(a.get("name"), a.get("website"), a.get("description"))
        return None

analysts = [
    {
        "name": "Larry C. Johnson",
        "website": "https://sonar21.com",
        "description": "Former CIA analyst & State Dept counterterrorism official; runs Sonar21 blog covering national security and global affairs from a skeptical, realist viewpoint."
    },
    {
        "name": "Daniel L. Davis",
        "website": "https://19fortyfive.com",
        "description": "Retired US Army Lt. Colonel and defense fellow; contributes critical analysis on US military strategy, especially regarding Ukraine and budget."
    },
    {
        "name": "Ray McGovern",
        "website": "https://consortiumnews.com",
        "description": "27-year CIA analyst turned independent; co-founder of Veteran Intelligence Professionals for Sanity; writes critical open-source intel assessments."
    },
    {
        "name": "Philip Giraldi",
        "website": "https://www.unz.com/author/philip-giraldi/",
        "description": "Former CIA case/military intel officer; now security consultant and columnist; directs Council for the National Interest; anti-interventionist realism."
    },
    {
        "name": "Andrei Martyanov",
        "website": "https://turcopolier.typepad.com",
        "description": "Former Soviet naval officer and military analyst; runs 'Reminiscence of the Future' blog, focusing on Russian vs US military-industrial realities."
    },
    {
        "name": "Chas W. Freeman Jr.",
        "website": "https://chasfreeman.net",
        "description": "Retired US diplomat and China/Middle East expert; realist voice on geopolitics; archives speeches/articles critical of US policy."
    },
    {
        "name": "Alastair Crooke",
        "website": "https://www.eurasiareview.com/author/alastair-crooke/",
        "description": "Ex-MI6 diplomat and founder of Conflicts Forum (Beirut); publishes deep Middle East and great-power essays independent of Western institutional frames."
    },
    {
        "name": "Patrick Armstrong",
        "website": "https://patrickarmstrong.ca/",
        "description": "Former Canadian diplomat in Moscow; independent analyst of Russia–West relations with realist, multipolar perspective."
    },
    {
        "name": "M. K. Bhadrakumar",
        "website": "https://indianpunchline.com",
        "description": "Retired Indian ambassador with deep Eurasia/Middle East experience; publishes sharp Global South realist commentary."
    },
    {
        "name": "Alex Krainer",
        "website": "https://alexkrainer.substack.com",
        "description": "Independent market & geopolitical analyst (Croatian background); author of The Naked Hedgie Substack, critical of mainstream financial-media narratives."
    },
    {
        "name": "Glenn Diesen",
        "website": "https://glenndiesen.substack.com",
        "description": "Norwegian political scientist, pro-multipolar realism; focuses on Russia, geoeconomics and critiques Western-led order."
    },
    {
        "name": "Mark Sleboda",
        "website": "https://marksleboda.substack.com",
        "description": "US Navy vet based in Moscow; hosts 'The Real Politick'; realist analysis of Russia–US tensions, often dismantling Western narratives."
    },
    {
        "name": "Chris Hedges",
        "website": "https://scheerpost.com",
        "description": "Pulitzer-winning journalist, ex–NYT war correspondent; radical realist and moral critique of empire; writes weekly and hosts Substack."
    },
    {
        "name": "Pepe Escobar",
        "website": "https://pepeescobar.substack.com",
        "description": "Brazilian Eurasia-focused journalist; covers multipolar world, China, BRICS; independent reporting blending on-the-ground insights."
    },
    {
        "name": "Patrick Lawrence",
        "website": "https://thefloutist.substack.com",
        "description": "Veteran foreign–affairs journalist; first to contest Russiagate; writes longform critique of US media, war policy, and establishment narratives."
    },
    {
        "name": "Caitlin Johnstone",
        "website": "https://caitlinjohnstone.substack.com",
        "description": "Australian satirical anti–war journalist; reader–funded Substack; challenges media propaganda and US/NATO interventions daily."
    },
    {
        "name": "Thierry Meyssan",
        "website": "https://voltairenet.org",
        "description": "French activist-journalist; founder of Voltaire Network; writes in French/English challenging Western media on war, disinformation, geopolitics."
    },
    {
        "name": "Elijah J. Magnier",
        "website": "https://ejmagnier.com",
        "description": "Veteran Middle East war correspondent; provides first-hand analysis of Syria, Iraq, Gaza; writes for The Cradle and personal blog."
    },
    {
        "name": "Jan Oberg",
        "website": "https://transnational.org",
        "description": "Swedish peace researcher and co–founder of Transnational Foundation; independent thought leadership on conflict resolution and non–violence."
    },
    {
        "name": "Moon of Alabama (Bernhard)",
        "website": "https://moonofalabama.org",
        "description": "Anonymous German blogger; daily open–source intelligence deep–dives, critical of NATO/Western media, widely followed by OSINT community."
    },
    {
        "name": "Boris Rozhin (Colonel Cassad)",
        "website": "https://colonelcassad.live",
        "description": "Russian military-history analyst; Crimea–based; provides minute–by–minute OSINT on Ukraine from pro–resistance, anti–NATO viewpoint."
    },
    {
        "name": "Jeffrey Sachs",
        "website": "https://www.commondreams.org/author/jeffrey-d-sachs",
        "description": "Columbia economist and former UN advisor; writes on global development, sustainable multipolarity; frequently published via Project Syndicate & Consortium News."
    },
    {
        "name": "Glenn Greenwald",
        "website": "https://greenwald.substack.com",
        "description": "Pulitzer-winner, ex–Intercept co–founder; focuses on surveillance, civil liberties, media critique and relentless foreign–policy skepticism."
    },
    {
        "name": "Max Blumenthal",
        "website": "https://thegrayzone.com",
        "description": "Investigative journalist and filmmaker; founder of The Grayzone; covers Middle East, media bias, imperialism and regime-change narratives."
    },
    {
        "name": "John Pilger",
        "website": "https://consortiumnews.com",
        "description": "Veteran Australian journalist and filmmaker; writes long-form critiques of Western foreign policy via personal site and Consortium News."
    },
    {
        "name": "Binoy Kampmark",
        "website": "https://counterpunch.org/author/jete6/",
        "description": "Cambridge–educated researcher at RMIT; writes widely on imperialism, international law, Australia's role; publishes at CounterPunch, ZNetwork, The Mandarin."
    },
    {
        "name": "Rana Abou Rjeily",
        "website": "https://ranahabib.substack.com",
        "description": "Lebanese writer and typographer based in Beirut; Substack offers cultural/political reflections from Middle East intersectional angle."
    }
]

def get_analyst_objects():
    return [Analyst(a["name"], a["website"], a["description"]) for a in analysts]
