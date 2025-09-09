import os
from datetime import date
import json
import sys
from string import Template
import time
from twikit import Client
import asyncio

def add_scores(json_path):
    with open(json_path, 'r') as file:
        data = json.load(file)[0]

    # Preprocessing
    if data["Third row seats"] == 0:
        data["Third row 3-point belt"] = "NA"
        data["Third row visual"] = "NA"
        data["Third row acoustic"] = "NA"
        data["Third row occupant detection"] = "NA"
        data["Third row immediate activation"] = "NA"
        data["Third row curtain airbag"] = "NA"
        data["Third row thorax airbag"] = "NA"
        data["Third row head restraint"] = "NA"
        data["Third row ISOFIX"] = "NA"
        data["Third row i-Size"] = "NA"
        data["Third row Top Tether"] = "NA"
    if data["Second row seats"] < 3:
        data["Centre 3-point belt"] = "NA"
        data["Centre visual"] = "NA"
        data["Centre acoustic"] = "NA"
        data["Centre occupant detection"] = "NA"
        data["Centre immediate activation"] = "NA"
        data["Centre head restraint"] = "NA"
        data["Centre ISOFIX"] = "NA"
        data["Centre i-Size"] = "NA"
        data["Centre Top Tether"] = "NA"
    
    data["PS_ESC"] = 8.0 if data["ESC"] == "YES" else 0.0
    data["PS_DMS"] = 2.0 if data["DMS"] == "YES" else 0.0
    data["PS_BSM"] = (1.0 if data["BSM passenger side"] == "YES" else 0.0) + (1.0 if data["BSM driver side"] == "YES" else 0.0)
    data["PS_TPMS"] = 2.0 if data["TPMS warning"] == "YES" else 0.0
    data["PS_physical_controls"] = (1.0 if data["Physical hazard lights"] == "YES" else 0.0) + (1.0 if data["Physical turn indicators"] == "YES" else 0.0) + (1.0 if data["Physical windscreen wipers"] == "YES" else 0.0) + (1.0 if data["Physical gear selector"] == "YES" else 0.0) + (1.0 if data["Physical climate controls"] == "YES" or data["Physical climate controls"] == "NA" else 0.0) + (1.0 if data["Physical music and navigation controls"] == "YES" or data["Physical music and navigation controls"] == "NA" else 0.0)

    # Validations
    if not data["ESC"] == "YES": data["ESC system name"] = "---"
    if not data["ESC"] == "YES": data["PS_ESC"] = 0.0

    if not data["BSM"] == "YES": data["BSM system name"] = "---"; data["BSM sensor"] = "---"
    if not data["BSM"] == "YES": data["PS_BSM"] = 0.0

    if not data["DMS"] == "YES": data["DMS system name"] = "---"
    if not data["DMS"] == "YES": data["PS_DMS"] = 0.0

    if not data["TPMS"] == "YES": data["TPMS system name"] = "---"
    if not data["TPMS"] == "YES": data["PS_TPMS"] = 0.0

    data["PS"] = data["PS_ESC"] + data["PS_BSM"] + data["PS_DMS"] + data["PS_TPMS"] + data["PS_physical_controls"]

    total_rear_seats = data["Second row seats"] + data["Third row seats"]

    if data["Third row seats"] > 0:
        if data["Second row seats"] == 3:
            data["SS_rear_seatbelts"] = 4.0 if data["Outboard 3-point belt"] == "YES" and data["Centre 3-point belt"] == "YES" and data["Third row 3-point belt"] == "YES" else 0.0
        elif data["Second row seats"] == 2:
            data["SS_rear_seatbelts"] = 4.0 if data["Outboard 3-point belt"] == "YES" and data["Third row 3-point belt"] == "YES" else 0.0
    else:
        if data["Second row seats"] == 3:
            data["SS_rear_seatbelts"] = 4.0 if data["Outboard 3-point belt"] == "YES" and data["Centre 3-point belt"] == "YES" else 0.0
        elif data["Second row seats"] == 2:
            data["SS_rear_seatbelts"] = 4.0 if data["Outboard 3-point belt"] == "YES" else 0.0
    
    if data["Third row seats"] > 0:
        if data["Second row seats"] == 3:
            data["SS_rear_seatbelt_reminders"] = 2.0 if data["Outboard visual"] == "YES" and data["Outboard acoustic"] == "YES" and data["Centre visual"] == "YES" and data["Centre acoustic"] == "YES" and data["Third row visual"] == "YES" and data["Third row acoustic"] == "YES" else 0.0
        elif data["Second row seats"] == 2:
            data["SS_rear_seatbelt_reminders"] = 2.0 if data["Outboard visual"] == "YES" and data["Outboard acoustic"] == "YES" and data["Third row visual"] == "YES" and data["Third row acoustic"] == "YES" else 0.0
    else:
        if data["Second row seats"] == 3:
            data["SS_rear_seatbelt_reminders"] = 2.0 if data["Outboard visual"] == "YES" and data["Outboard acoustic"] == "YES" and data["Centre visual"] == "YES" and data["Centre acoustic"] == "YES" else 0.0
        elif data["Second row seats"] == 2:
            data["SS_rear_seatbelt_reminders"] = 2.0 if data["Outboard visual"] == "YES" and data["Outboard acoustic"] == "YES" else 0.0

    num_seats_seatbelt_reminder_passed = 0
    if data["Outboard visual"] == "YES" and data["Outboard acoustic"] == "YES" and data["Outboard occupant detection"] == "YES" and data["Outboard immediate activation"] == "YES":
        num_seats_seatbelt_reminder_passed += 2
    if data["Second row seats"] > 2 and data["Centre visual"] == "YES" and data["Centre acoustic"] == "YES" and data["Centre occupant detection"] == "YES" and data["Centre immediate activation"] == "YES":
        num_seats_seatbelt_reminder_passed += 1
    if data["Third row seats"] > 0 and data["Third row visual"] == "YES" and data["Third row acoustic"] == "YES" and data["Third row occupant detection"] == "YES" and data["Third row immediate activation"] == "YES":
        num_seats_seatbelt_reminder_passed += data["Third row seats"]

    data["SS_rear_seatbelt_reminders"] += 8 * (num_seats_seatbelt_reminder_passed / total_rear_seats)

    if data["Third row seats"] > 0:
        if data["Second row seats"] == 3:
            data["SS_head_restraints"] = 4.0 if data["Outboard head restraint"] == "YES" and data["Centre head restraint"] == "YES" and data["Third row head restraint"] == "YES" else 0.0
        elif data["Second row seats"] == 2:
            data["SS_head_restraints"] = 4.0 if data["Outboard head restraint"] == "YES" and data["Third row head restraint"] == "YES" else 0.0
    else:
        if data["Second row seats"] == 3:
            data["SS_head_restraints"] = 4.0 if data["Outboard head restraint"] == "YES" and data["Centre head restraint"] == "YES" else 0.0
        elif data["Second row seats"] == 2:
            data["SS_head_restraints"] = 4.0 if data["Outboard head restraint"] == "YES" else 0.0
    
    if data["Third row seats"] > 0:
        if data["Front curtain airbag"] == "YES":
            data["SS_side_head_airbags"] = 5.0 if data["Third row curtain airbag"] == "YES" and data["Rear curtain airbag"] == "YES" else 3.0
        else:
            data["SS_side_head_airbags"] = 0.0
    else:
        if data["Front curtain airbag"] == "YES":
            data["SS_side_head_airbags"] = 5.0 if data["Rear curtain airbag"] == "YES" else 3.0
        else:
            data["SS_side_head_airbags"] = 0.0
        

    data["SS_side_head_airbags"] += 1.0 if data["Front far side airbag"] == "YES" else 0.0

    data["SS_side_thorax_airbags"] = (2.0 if data["Front thorax airbag"] == "YES" else 0.0) + (1.0 if data["Rear thorax airbag"] == "YES" else 0.0)

    data["SS_child_readiness"] = (1.0 if data["Outboard ISOFIX"] == "YES" else 0.0) + (0.5 if data["Centre ISOFIX"] == "YES" else 0.0) + (0.5 if data["Front passenger ISOFIX"] == "YES" else 0.0) + (1.0 if data["Third row ISOFIX"] == "YES" else 0.0)
    data["SS_child_readiness"] += (0.5 if data["Outboard i-Size"] == "YES" else 0.0) + (0.25 if data["Centre i-Size"] == "YES" else 0.0) + (0.25 if data["Front passenger i-Size"] == "YES" else 0.0) + (0.5 if data["Third row i-Size"] == "YES" else 0.0)
    data["SS_child_readiness"] += (0.5 if data["Outboard Top Tether"] == "YES" else 0.0) + (0.25 if data["Centre Top Tether"] == "YES" else 0.0) + (0.25 if data["Front passenger Top Tether"] == "YES" else 0.0) + (0.5 if data["Third row Top Tether"] == "YES" else 0.0)
    data["SS_child_readiness"] = min(data["SS_child_readiness"], 3.0)

    data["SS"] = data["SS_rear_seatbelts"] + data["SS_rear_seatbelt_reminders"] + data["SS_head_restraints"] + data["SS_side_head_airbags"] + data["SS_side_thorax_airbags"] + data["SS_child_readiness"]

    data["PS"] /= 0.2
    data["PS"] = int(data["PS"])
    data["SS"] /= 0.3
    data["SS"] = int(data["SS"])

    ps, ss = data["PS"], data["SS"]

    data["PS_stars"] = 5 if ps >= 90 else 4 if ps >= 70 else 3 if ps >= 50 else 2 if ps >= 30 else 1 if ps >= 10 else 0
    data["SS_stars"] = 5 if ss >= 90 else 4 if ss >= 70 else 3 if ss >= 50 else 2 if ss >= 30 else 1 if ss >= 10 else 0

    data["stars"] = min(data["PS_stars"], data["SS_stars"])

    return data

def generate_report(data: dict):
    def dot(value):
        if value == "YES":
            return r"\statuscircle{2}"
        elif value == "NO":
            return r"\statuscircle{1}"
        else:
            return r"\statuscircle{0}"
    
    with open("template.tex", 'r') as file:
        template = Template(file.read())
        
    report_content = template.substitute(
        make=data["Manufacturer"],
        model=data["Model"],
        equipment=data["Equipment"],
        variant=data["Variant"],
        stars=data["stars"],
        image_path=data["Image"],

        PS=data["PS"],

        PS_ESC=data["PS_ESC"],
        PS_DMS=data["PS_DMS"],
        PS_TPMS=data["PS_TPMS"],
        PS_BSM=data["PS_BSM"],
        PS_physical_controls=data["PS_physical_controls"],
        
        ESC_system_name=data["ESC system name"],

        DMS_system_name=data["DMS system name"],

        TPMS_system_name=data["TPMS system name"],
        TPMS_warning=dot(data["TPMS warning"]),
        TPMS_readout=dot(data["TPMS readout"]),

        BSM_system_name=data["BSM system name"],
        BSM_sensor=data["BSM sensor"],
        BSM_driver=dot(data["BSM driver side"]),
        BSM_passenger=dot(data["BSM passenger side"]),

        hazard=dot(data["Physical hazard lights"]),
        indicators=dot(data["Physical turn indicators"]),
        wipers=dot(data["Physical windscreen wipers"]),
        gear=dot(data["Physical gear selector"]),
        climate=dot(data["Physical climate controls"]),
        music=dot(data["Physical music and navigation controls"]),


        SS=data["SS"],
        
        SS_seatbelts=data["SS_rear_seatbelts"],
        SS_sbr=data["SS_rear_seatbelt_reminders"],
        SS_curtainairbags=data["SS_side_head_airbags"],
        SS_thoraxairbags=data["SS_side_thorax_airbags"],
        SS_headrestraints=data["SS_head_restraints"],
        SS_child=data["SS_child_readiness"],

        threeptoutboard=dot(data["Outboard 3-point belt"]),
        threeptcentre=dot(data["Centre 3-point belt"]),
        threeptthirdrow=dot(data["Third row 3-point belt"]),

        visual_outboard=dot(data["Outboard visual"]),
        visual_centre=dot(data["Centre visual"]),
        visual_thirdrow=dot(data["Third row visual"]),
        acoustic_outboard=dot(data["Outboard acoustic"]),
        acoustic_centre=dot(data["Centre acoustic"]),
        acoustic_thirdrow=dot(data["Third row acoustic"]),
        detection_outboard=dot(data["Outboard occupant detection"]),
        detection_centre=dot(data["Centre occupant detection"]),
        detection_thirdrow=dot(data["Third row occupant detection"]),
        immediate_outboard=dot(data["Outboard immediate activation"]),
        immediate_centre=dot(data["Centre immediate activation"]),
        immediate_thirdrow=dot(data["Third row immediate activation"]),

        frontcurtainairbag=dot(data["Front curtain airbag"]),
        rearcurtainairbag=dot(data["Rear curtain airbag"]),
        thirdrowcurtainairbag=dot(data["Third row curtain airbag"]),
        frontfarsideairbag=dot(data["Front far side airbag"]),
        frontthoraxairbag=dot(data["Front thorax airbag"]),
        rearthoraxairbag=dot(data["Rear thorax airbag"]),

        headrest_outboard=dot(data["Outboard head restraint"]),
        headrest_centre=dot(data["Centre head restraint"]),
        headrest_thirdrow=dot(data["Third row head restraint"]),

        isofix_outboard=dot(data["Outboard ISOFIX"]),
        isofix_centre=dot(data["Centre ISOFIX"]),
        isofix_front=dot(data["Front passenger ISOFIX"]),
        isofix_thirdrow=dot(data["Third row ISOFIX"]),
        isize_outboard=dot(data["Outboard i-Size"]),
        isize_centre=dot(data["Centre i-Size"]),
        isize_front=dot(data["Front passenger i-Size"]),
        isize_thirdrow=dot(data["Third row i-Size"]),
        tether_outboard=dot(data["Outboard Top Tether"]),
        tether_centre=dot(data["Centre Top Tether"]),
        tether_front=dot(data["Front passenger Top Tether"]),
        tether_thirdrow=dot(data["Third row Top Tether"]),


        comments=data["Comments"],
        PS_stars=data["PS_stars"],
        SS_stars=data["SS_stars"]
    )

    if not os.path.exists("tex_source"):
        os.mkdir("tex_source")

    name = "-".join([date.today().strftime('%Y-%m-%d'), data["Manufacturer"], data["Model"], data["Equipment"], "equipment", str(data["stars"]), "star"])
    output_path = os.path.join("tex_source", "".join(c for c in name if c.isalpha() or c.isdigit() or c=='-' or c=='_' or c==' ')+".tex")

    with open(output_path, 'w') as file:
        file.write(report_content)
        print("Report LaTeX source code is in", output_path)
    
    return output_path

def compile_latex(tex_path):
    if not os.path.exists("cdn"):
        os.mkdir("cdn")
    os.system(f'pdflatex -output-directory=cdn "{tex_path}"')
    os.system(f"find cdn -maxdepth 1 -type f ! -name '*.pdf' -delete")

def update_page():
    with open("template.html", 'r') as file:
        template = Template(file.read())
    
    webpage_content = template.substitute(
        results="".join([f"<li><a href=\"cdn/{filename}\">{filename.replace('.pdf', '').replace('-', ' ')}</a></li>\n" for filename in sorted(os.listdir("cdn"), reverse=True)]),
        count=len(os.listdir("cdn"))
    )

    with open("index.html", "w") as file:
        file.write(webpage_content)

def add_to_summary(data):
    with open("summary.json", 'r') as file:
        existing_data = json.load(file)
    
    with open("summary.json", 'w') as file:
        existing_data.append({"Manufacturer": data["Manufacturer"], "Model": data["Model"], "Equipment": data["Equipment"], "PS": data["PS"], "SS": data["SS"], "stars": data["stars"]})
        existing_data = sorted(existing_data, key=lambda x: (x["stars"], 0.2*x["PS"]+0.3*x["SS"], x["SS"], x["PS"]), reverse=True)
        json.dump(existing_data, file, indent=4)
    
    with open("tex_source/summary.tex", 'w') as file:
        template_str = r"""
\documentclass[letterpaper, landscape]{scrartcl}
\usepackage{fleetsure}
\usepackage{longtable}
\begin{document}
\sffamily
\noindent \Huge \textbf{\href{https://theyawninchihua.github.io/fleetsure/}{FleetSure}} \hfill \includegraphics[height=1.5em]{images/logo_3d.png}\\
\noindent \LARGE Protocol v1.0 • results until \today\\

\centering
\LARGE
\rmfamily
\begin{longtable}{| p{.40\textwidth} | p{.15\textwidth} | p{.12\textwidth} | p{.12\textwidth} | p{.15\textwidth} |}
\sffamily \textbf{model}& \sffamily \textbf{equipment} & \sffamily \textbf{primary} & \sffamily \textbf{secondary} & \sffamily \textbf{result}\\
\hline
\hline
$results
\end{longtable}
\end{document} 
"""
        template = Template(template_str)
        summary_content = template.substitute(
            results="".join(f'{result["Manufacturer"]} \\bfseries {result["Model"]}\\mdseries & {result["Equipment"]} & \\sffamily {result["PS"]}\\% & \\sffamily {result["SS"]}\\% & \\starrating{result["stars"]}\\\\\\hline\n' for result in existing_data)
        )
        file.write(summary_content)



def create_tweet(data: dict):
    if not os.path.exists("tweets"):
        os.mkdir("tweets")
    
    name = "-".join([date.today().strftime('%Y-%m-%d'), data["Manufacturer"], data["Model"], data["Equipment"], "equipment", str(data["stars"]), "star"])
    pdf_path = os.path.join("cdn", "".join(c for c in name if c.isalpha() or c.isdigit() or c=='-' or c=='_' or c==' ')+".pdf")
    text_path = os.path.join("tweets", "".join(c for c in name if c.isalpha() or c.isdigit() or c=='-' or c=='_' or c==' ')+".txt")
    image_path = os.path.join("tweets", "".join(c for c in name if c.isalpha() or c.isdigit() or c=='-' or c=='_' or c==' ')+".png")

    with open(text_path, "w") as file:
        file.write("New #FleetSure results\n")
        file.write("\n")
        file.write(f"{data['Manufacturer']} {data['Model']}\n")
        file.write(f"with {data['Equipment']} equipment")
        file.write("\n")
        for i in range(data["stars"]):
            file.write(f"⭐️")
        file.write("\n")
        file.write(f"{data['stars']} stars\n")
        file.write("\n")
        file.write("More: https://theyawninchihua.github.io/fleetsure/")
    
    os.system(f"sips -s format png \"{pdf_path}\" --out \"{image_path}\"")

    return text_path, image_path

async def publish_tweet(text_path, image_path):
    client = Client('en-US')
    client.load_cookies("gobarncrap.json")

    with open(text_path, "r", encoding="utf-8") as file:
        tweet_text = file.read()
        media_ids = [await client.upload_media(image_path)]
        await client.create_tweet(text=tweet_text, media_ids=media_ids)

if __name__ == "__main__":
    # usage: python rate_vehicles.py data/car1.json data/car2.json ...
    json_files = sys.argv[1:]
    for json_file in json_files:
        data = add_scores(json_file)
        tex_path = generate_report(data)
        compile_latex(tex_path) # COMMENT OUT IF pdflatex NOT INSTALLED
        update_page()
        add_to_summary(data)
        compile_latex("tex_source/summary.tex")

        txt, png = create_tweet(data) # COMMENT OUT IF sips NOT INSTALLED (SHIPS WITH MACOS) OR twikit NOT INSTALLED
        
        input(f"Tweet {data['Model']} {data['Equipment']}?")
        asyncio.run(publish_tweet(txt, png))