from configparser import ConfigParser

config_writer = ConfigParser()

config_writer["r"] = {
    "rendrill": 1051071428520312852,
    "unverified": 1050849258418471003,
    "muted": 1061970447031345192,
    "guardrill": 1051071831706193951,
    "explorill": 1051072126729342986,
    "liberator": 1051070723067756604,
    "purmarill": 1051144944137556019,
    "promdrill": 1063099505806942299
}

config_writer["c"] = {
    "welcome": 1050853430824022200,
    "verification": 1050848928456785990,
    "rendrill": 1061970102775463976,
    "levelup": 1071876917168455801,
    "log": 1052258308007936082,
    "member_stats": 1052251057176191036,
    "purmarill": 1061970044441075753,
    "command": 1051065222883975228,
    "flr_stats": 1071861905691525220,
    "mint_date": 1071522299292946522,
    "roadmap": 1052255880613208145,
    "mint": 1071522299292946522,
    "explorill": 1070698304217821204,
    "promdrill": 1070700811396591637,
    "spinwheel": 1070742662551961640,
    "past_members": 1073558733529034802,
    "general": 1069251795194482728,
    "official_links": 1071893999197098147
}

config_writer["t"] = {
    "channel": 1051064803025760346,
    "account": "TheMandrillsNFT",
    "tweet-id": 0,
    "update": 5
}

config_writer["x"] = {
    "difficulty": 1.6
}

config_writer["col"] = {
    "hex1": "#FF66CC",
    "hex2": "#0000D8",
    "base": 15544212

}

with open("./data/config.ini", 'w') as f:
    config_writer.write(f)