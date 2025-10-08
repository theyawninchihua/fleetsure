import sys
import os
from moviepy import *
from rate_vehicles import add_scores
from markovmusic import MarkovComposer

DOT_GREEN = "video_elements/dotgreen.png"
DOT_RED = "video_elements/dotred.png"
DOT_EMPTY = "video_elements/dotempty.png"

def make_table_slide(brand: str, model: str, equipment: str, title: str, content: dict[str, list[str]]):
    # Background and fixed branding
    bg = ColorClip(size=(1280, 720), color=(255, 255, 255)).with_duration(5)

    logo = TextClip(
        font="video_elements/cm/cmunrm.ttf",
        text=f"{brand} {model} ({equipment})",
        font_size=40,
        color="black"
    ).with_position((60, 60)).with_duration(5)

    fleetsure = TextClip(
        font="video_elements/cm/cmunss.ttf",
        text="FleetSure v1.0",
        font_size=40,
        color="black"
    ).with_position((980, 60)).with_duration(5)

    # Title
    title_clip = TextClip(
        text=title,
        font="video_elements/cm/cmunss.ttf",
        font_size=50,
        color="black"
    ).with_position((60, 150)).with_duration(5).with_effects([vfx.FadeIn(1, initial_color = [255, 255, 255])])

    # Separator line (use a thin rectangle)
    line_clip = ColorClip(size=(1160, 3), color=(0, 0, 0)).with_position((60, 210)).with_duration(5).with_effects([vfx.FadeIn(0.4, initial_color = [255, 255, 255])])

    # Build table rows
    table_clips = []
    start_y = 250
    row_height = 60

    for row_idx, (key, values) in enumerate(content.items()):
        y = start_y + row_idx * row_height

        # Left column: the key
        key_clip = TextClip(
            text=key,
            font="video_elements/cm/cmunss.ttf",
            font_size=35,
            color="black"
        ).with_position((100, y)).with_start(1).with_duration(4).with_effects([vfx.FadeIn(1, initial_color = [255, 255, 255])])
        table_clips.append(key_clip)

        # Value columns
        for col_idx, val in enumerate(values):
            x = 450 + col_idx * 200

            if val == "YES":
                cell = ImageClip(DOT_GREEN).resized(height=30)
            elif val == "NO":
                cell = ImageClip(DOT_RED).resized(height=30)
            elif val == "NA":
                cell = ImageClip(DOT_EMPTY).resized(height=30)
            else:
                cell = TextClip(
                    text=str(val),
                    font="video_elements/cm/cmunss.ttf",
                    font_size=30,
                    color="black"
                ).with_start(1)

            # Center the dot/text vertically in the row
            cell = cell.with_position((x, y)).with_start(2).with_duration(3).with_effects([vfx.FadeIn(1, initial_color = [255, 255, 255])])
            table_clips.append(cell)

    return CompositeVideoClip(
        [bg, logo, fleetsure, title_clip, line_clip] + table_clips,
        size=(1280, 720)
    )

def make_intro(brand, model, equipment, stars, image_path):
    def star_rating(rating, size=100, y=360, x=60, spacing=0, start=2, duration=3):
        stars = []
        for i in range(5):
            path = "video_elements/starfull.png" if i < rating else "video_elements/starempty.png"
            img = ImageClip(path).resized(height=size).with_start(start+i*(duration/5)).with_duration(duration * (1 - i/5)).with_effects([vfx.FadeIn(0.4, initial_color = [255, 255, 255])])
            img = img.with_position((x + i*(size+spacing), y))
            stars.append(img)
        return stars
    bg = ColorClip(size=(1280, 720), color=(255,255,255)).with_duration(5)
    logo = ImageClip("../logo_3d.png").resized(height=70).with_position((60, 60)).with_start(0).with_duration(5)
    fleetsure = TextClip(font="video_elements/cm/cmunss.ttf", text="FleetSure v1.0", font_size=40).with_position((980, 60)).with_start(0).with_duration(5)
    img = ImageClip(image_path).resized(height=300).with_position((640, 200)).with_start(0).with_duration(5).with_effects([vfx.FadeIn(2)])
    name = TextClip(font="video_elements/cm/cmunrm.ttf", text=brand+" "+model, font_size=70).with_position((60, 200)).with_start(1).with_duration(4)
    equipment = TextClip(font="video_elements/cm/cmunrm.ttf", text=equipment+" safety equipment", font_size=40).with_position((60, 275)).with_start(1).with_duration(4)
    stars = star_rating(stars)
    return CompositeVideoClip([bg, logo, fleetsure, img, name, equipment]+stars)

def make_summary(brand, model, equipment, variant, ps, ss, ps_stars, ss_stars, stars):
    bg = ColorClip(size=(1280, 720), color=(255,255,255)).with_duration(5)
    logo = TextClip(font="video_elements/cm/cmunrm.ttf", text=brand+" "+model+" ("+equipment+")", font_size=40).with_position((60, 60)).with_start(0).with_duration(5)
    fleetsure = TextClip(font="video_elements/cm/cmunss.ttf", text="FleetSure v1.0", font_size=40).with_position((980, 60)).with_start(0).with_duration(5)
    def overall_star_rating(rating, size=95, y=150, x=400, spacing=0):
        stars = []
        for i in range(5):
            path = "video_elements/starfull.png" if i < rating else "video_elements/starempty.png"
            img = ImageClip(path).resized(height=size).with_start(0).with_duration(5).with_effects([vfx.FadeIn(1, initial_color = [255, 255, 255])])
            img = img.with_position((x + i*(size+spacing), y))
            stars.append(img)
        return stars
    overall_stars = overall_star_rating(stars)
    def sub_star_rating(rating, size, y, x, spacing, start, duration):
        stars = []
        for i in range(5):
            path = "video_elements/starfull.png" if i < rating else "video_elements/starempty.png"
            img = ImageClip(path).resized(height=size).with_start(start+i*(duration/5)).with_duration(duration * (1 - i/5)).with_effects([vfx.FadeIn(0.8, initial_color = [255, 255, 255])])
            img = img.with_position((x + i*(size+spacing), y))
            stars.append(img)
        return stars
    primary_stars = sub_star_rating(ps_stars, 40, 300, 680, 0, 1, 4)
    # primary_perc = TextClip(font="video_elements/cm/cmunss.ttf", text=f"{ps}%", font_size=18).with_position((770, 350)).with_start(0).with_duration(5).with_effects([vfx.FadeIn(1, initial_color = [255, 255, 255])])
    secondary_stars = sub_star_rating(ss_stars, 40, 400, 680, 0, 1, 4)
    # secondary_perc = TextClip(font="video_elements/cm/cmunss.ttf", text=f"{ss}%", font_size=18).with_position((770, 450)).with_start(0).with_duration(5).with_effects([vfx.FadeIn(1, initial_color = [255, 255, 255])])
    primary = TextClip(font="video_elements/cm/cmunss.ttf", text="primary safety", font_size=36).with_position((400, 300)).with_start(0).with_duration(5).with_effects([vfx.FadeIn(1, initial_color = [255, 255, 255])])
    secondary = TextClip(font="video_elements/cm/cmunss.ttf", text="secondary safety", font_size=36).with_position((400, 400)).with_start(0).with_duration(5).with_effects([vfx.FadeIn(1, initial_color=[255, 255, 255]), vfx.FadeOut(2, final_color = [255, 255, 255])])
    variant_clip = TextClip(font="video_elements/cm/cmunss.ttf", text="Variant evaluated: "+variant, font_size=40).with_position(("center", 540)).with_start(0).with_duration(5).with_effects([vfx.FadeIn(1, initial_color=[255, 255, 255]), vfx.FadeOut(2, final_color = [255, 255, 255])])
    return CompositeVideoClip([bg, logo, fleetsure, primary, secondary, variant_clip]+primary_stars+secondary_stars+overall_stars)

def make_section_intro(brand, model, equipment, section, perc, stars):
    bg = ColorClip(size=(1280, 720), color=(255,255,255)).with_duration(5)
    logo = TextClip(font="video_elements/cm/cmunrm.ttf", text=brand+" "+model+" ("+equipment+")", font_size=40).with_position((60, 60)).with_start(0).with_duration(5)
    fleetsure = TextClip(font="video_elements/cm/cmunss.ttf", text="FleetSure v1.0", font_size=40).with_position((980, 60)).with_start(0).with_duration(5)
    def sub_star_rating(rating, size, y, x, spacing):
        stars = []
        for i in range(5):
            path = "video_elements/starfull.png" if i < rating else "video_elements/starempty.png"
            img = ImageClip(path).resized(height=size).with_start(0).with_duration(5).with_effects([vfx.FadeOut(2, final_color = [255, 255, 255])])
            img = img.with_position((x + i*(size+spacing), y))
            stars.append(img)
        return stars
    primary_stars = sub_star_rating(stars, 40, 300, 680, 0)
    primary_perc = TextClip(font="video_elements/cm/cmunss.ttf", text=f"{perc}%", font_size=40).with_position((750, 350)).with_start(0).with_duration(5).with_effects([vfx.FadeIn(1, initial_color=[255, 255, 255]), vfx.FadeOut(2, final_color = [255, 255, 255])])
    primary = TextClip(font="video_elements/cm/cmunss.ttf", text=section, font_size=36).with_position((400, 300)).with_start(0).with_duration(5).with_effects([vfx.FadeOut(2, final_color = [255, 255, 255])])
    return CompositeVideoClip([bg, logo, fleetsure, primary, primary_perc]+primary_stars)

def make_outro():
    bg = ColorClip(size=(1280, 720), color=(255,255,255)).with_duration(5)
    logo = ImageClip("../logo_3d.png").resized(height=200).with_position(("center", 150)).with_start(0).with_duration(5)
    fleetsure = TextClip(font="video_elements/cm/cmunss.ttf", text="FleetSure v1.0", font_size=70).with_position(("center", 420)).with_start(0).with_duration(5)
    return CompositeVideoClip([bg, logo, fleetsure])

if __name__ == "__main__":
    # usage: python make_videos.py data/car1.json data/car2.json ...
    json_files = sys.argv[1:]
    for json_file in json_files:
        data = add_scores(json_file)
        intro = make_intro(data["Manufacturer"], data["Model"], data["Equipment"], data["stars"], data["Image"])
        summary = make_summary(data["Manufacturer"], data["Model"], data["Equipment"], data["Variant"], data["PS"], data["SS"], data["PS_stars"], data["SS_stars"], data["stars"])

        ps_intro = make_section_intro(data["Manufacturer"], data["Model"], data["Equipment"], "primary safety", data["PS"], data["PS_stars"])
        esc = make_table_slide(data["Manufacturer"], data["Model"], data["Equipment"], f"Electronic Stability Control ({data['PS_ESC']} max. 8)", {"fitted": [data['ESC']], "system name": [data['ESC system name']]})
        dms = make_table_slide(data["Manufacturer"], data["Model"], data["Equipment"], f"Driver Monitoring ({data['PS_DMS']} max. 2)", {"fitted": [data['DMS']], "system name": [data['DMS system name']]})
        tpms = make_table_slide(data["Manufacturer"], data["Model"], data["Equipment"], f"Tyre Pressure Monitoring ({data['PS_TPMS']} max. 2)", {"fitted": [data['TPMS']], "system name": [data['TPMS system name']], "warning": [data['TPMS warning']], "readout": [data['TPMS readout']]})
        bsm = make_table_slide(data["Manufacturer"], data["Model"], data["Equipment"], f"Blind Spot Monitoring ({data['PS_BSM']} max. 2)", {"fitted": [data['BSM']], "system name": [data['BSM system name']], "input": [data['BSM sensor']], "driver side": [data['BSM driver side']], "passenger side": [data['BSM passenger side']]})
        phy_con = make_table_slide(data["Manufacturer"], data["Model"], data["Equipment"], f"Physical Controls ({data['PS_physical_controls']} max. 6)", {"hazard lights": [data['Physical hazard lights']], "gear": [data['Physical gear selector']], "climate": [data['Physical climate controls']], "music and navigation": [data['Physical music and navigation controls']], "turn indicators": [data['Physical turn indicators']], "windscreen wipers": [data['Physical windscreen wipers']]})

        ss_intro = make_section_intro(data["Manufacturer"], data["Model"], data["Equipment"], "secondary safety", data["SS"], data["SS_stars"])
        seatbelt = make_table_slide(data["Manufacturer"], data["Model"], data["Equipment"], f"Rear Seatbelts ({data['SS_rear_seatbelts']} max. 4)", {"position": ["outboard", "centre", "third row"], "three-point": [data['Outboard 3-point belt'], data['Centre 3-point belt'], data['Third row 3-point belt']]})
        sbr = make_table_slide(data["Manufacturer"], data["Model"], data["Equipment"], f"Rear Seatbelt Reminders ({data['SS_rear_seatbelt_reminders']} max. 10)", {"position": ["outboard", "centre", "third row"], "visual signal": [data['Outboard visual'], data['Centre visual'], data['Third row visual']], "acoustic signal": [data['Outboard acoustic'], data['Centre acoustic'], data['Third row acoustic']], "occupant detection": [data['Outboard occupant detection'], data['Centre occupant detection'], data['Third row occupant detection']], "immediate activation": [data['Outboard immediate activation'], data['Centre immediate activation'], data['Third row immediate activation']]})
        curtainab = make_table_slide(data["Manufacturer"], data["Model"], data["Equipment"], f"Head Protection Devices ({data['SS_side_head_airbags']} max. 6)", {"position": ["front", "rear", "third row"], "curtain airbag": [data['Front curtain airbag'], data['Rear curtain airbag'], data['Third row curtain airbag']], "centre airbag": [data["Front far side airbag"], "NA", "NA"]})
        sideab = make_table_slide(data["Manufacturer"], data["Model"], data["Equipment"], f"Chest Protection Devices ({data['SS_side_thorax_airbags']} max. 3)", {"position": ["front", "rear"], "thorax airbag": [data['Front thorax airbag'], data['Rear thorax airbag']]})
        headrest = make_table_slide(data["Manufacturer"], data["Model"], data["Equipment"], f"Neck Restraints ({data['SS_head_restraints']} max. 4)", {"position": ["outboard", "centre", "third row"], "sufficient": [data['Outboard head restraint'], data['Centre head restraint'], data['Third row head restraint']]})
        child = make_table_slide(data["Manufacturer"], data["Model"], data["Equipment"], f"Child Readiness ({data['SS_child_readiness']} max. 3)", {"position": ["outboard", "centre", "front passenger", "third row"], "ISOFIX": [data['Outboard ISOFIX'], data['Centre ISOFIX'], data['Front passenger ISOFIX'], data['Third row ISOFIX']], "i-Size": [data['Outboard i-Size'], data['Centre i-Size'], data['Front passenger i-Size'], data['Third row i-Size']], "Top Tether": [data['Outboard Top Tether'], data['Centre Top Tether'], data['Front passenger Top Tether'], data['Third row Top Tether']]})

        outro = make_outro()

        video = concatenate_videoclips([intro, summary, ps_intro, esc, dms, tpms, bsm, phy_con, ss_intro, seatbelt, sbr, curtainab, sideab, headrest, child, outro])
        composer = MarkovComposer()
        composer.fit("video_elements/FLR.mid", look_back=2)
        try:
            composer.compose(wav_path="video_elements/FLR.wav", play=False)
            music = AudioFileClip("video_elements/FLR.wav").subclipped(0, video.duration + 1.2)
        except KeyError as e:
            print("[INFO] Markov chain starvation, falling back to pre-generated music.", flush=True, file=sys.stderr)
            music = AudioFileClip("video_elements/FLR_fallback.wav").subclipped(0, video.duration + 1.2)
        music = CompositeAudioClip([music])
        video = video.with_audio(music)

        name = "-".join([data["Manufacturer"], data["Model"], data["Equipment"], "equipment", str(data["stars"]), "star"])
        output_path = os.path.join("videos", "".join(c for c in name if c.isalpha() or c.isdigit() or c=='-' or c=='_' or c==' ')+".mp4")

        video.write_videofile(output_path, fps=24)