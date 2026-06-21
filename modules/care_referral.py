import json
from pathlib import Path
from config import URGENCY_EMERGENCY, URGENCY_HIGH, URGENCY_MEDIUM, URGENCY_LOW

# Bengali translations for facility tiers
FACILITY_TIERS_BN = {
    "community_clinic": {
        "description": "কমিউনিটি ক্লিনিক — বিনামূল্যে প্রাথমিক চিকিৎসা, বাড়ির সবচেয়ে কাছে",
        "when_to_go": "ছোটখাটো অসুস্থতা, নিয়মিত স্বাস্থ্য পরীক্ষা, পরিবার পরিকল্পনা, টিকাদান",
        "cost": "বিনামূল্যে"
    },
    "upazila_health_complex": {
        "description": "উপজেলা স্বাস্থ্য কমপ্লেক্স — বিনামূল্যে সরকারি হাসপাতাল",
        "when_to_go": "মাঝারি ধরনের অসুস্থতা, কমিউনিটি ক্লিনিক থেকে রেফারেল বা সাধারণ বহিঃবিভাগ",
        "cost": "বিনামূল্যে (সরকারি)"
    },
    "district_hospital": {
        "description": "জেলা সদর হাসপাতাল — বড় সরকারি চিকিৎসা কেন্দ্র",
        "when_to_go": "বিশেষজ্ঞ চিকিৎসকের পরামর্শ বা ছোটখাটো অস্ত্রোপচারের প্রয়োজন হলে",
        "cost": "খুবই সামান্য (সরকারি)"
    },
    "medical_college_hospital": {
        "description": "মেডিকেল কলেজ হাসপাতাল — বিশেষায়িত ও উন্নত চিকিৎসা",
        "when_to_go": "জটিল রোগ, গুরুতর অসুস্থতা বা উচ্চতর বিশেষজ্ঞ পরামর্শের জন্য",
        "cost": "খুবই সামান্য (সরকারি) অথবা পরিশোধিত (বেসরকারি)"
    }
}

def load_hospital_data() -> dict:
    hospital_path = Path("data/hospitals.json")
    if not hospital_path.exists():
        return {}
    with open(hospital_path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_referral(urgency: str, lang: str = "en") -> dict:
    """
    Returns care referral recommendation based on urgency level and language.
    """
    data = load_hospital_data()
    tiers = data.get("facility_tiers", {})
    emergency_numbers = data.get("emergency_numbers", {})
    urgency_map = data.get("urgency_to_facility", {})

    if urgency == URGENCY_EMERGENCY:
        return {
            "action": "EMERGENCY — Call 999 immediately or go to nearest hospital",
            "action_bn": "জরুরি অবস্থা — অবিলম্বে ৯৯৯ নম্বরে কল করুন বা নিকটস্থ হাসপাতালে যান",
            "call": emergency_numbers.get("national_emergency", "999"),
            "facility_type": "Emergency Department",
            "message_en": (
                "This is an emergency. Call **999** immediately or go to the nearest "
                "hospital emergency department. Do not wait."
            ),
            "message_bn": (
                "এটি একটি জরুরি অবস্থা। এখনই **৯৯৯** কল করুন অথবা নিকটস্থ "
                "হাসপাতালের জরুরি বিভাগে যান। দেরি করবেন না।"
            )
        }

    facility_key = urgency_map.get(urgency, "upazila_health_complex")
    facility_en = tiers.get(facility_key, {})
    facility_bn = FACILITY_TIERS_BN.get(facility_key, {})

    if lang == "bn":
        desc = facility_bn.get("description", "নিকটস্থ স্বাস্থ্য কেন্দ্র")
        when = facility_bn.get("when_to_go", "")
        cost = facility_bn.get("cost", "ভিন্ন হতে পারে")
        return {
            "action": f"যান: {desc}",
            "when_to_go": when,
            "cost": cost,
            "facility_type": facility_key,
            "dghs_hotline": emergency_numbers.get("dghs_hotline", "16401"),
            "message": (
                f"আপনার উপসর্গের ওপর ভিত্তি করে, আমরা আপনাকে একটি "
                f"**{desc}** পরিদর্শনের সুপারিশ করছি। "
                f"{when} খরচ: {cost}। "
                f"যেকোনো নির্দেশনার জন্য ডিজিএইচএস স্বাস্থ্য লাইনে কল করুন: **১৬৪০১**।"
            )
        }
    else:
        desc = facility_en.get("description", "nearest health facility")
        when = facility_en.get("when_to_go", "")
        cost = facility_en.get("cost", "varies")
        return {
            "action": f"Visit: {desc}",
            "when_to_go": when,
            "cost": cost,
            "facility_type": facility_key,
            "dghs_hotline": emergency_numbers.get("dghs_hotline", "16401"),
            "message": (
                f"Based on your symptoms, we recommend visiting a "
                f"**{desc}**. "
                f"{when} Cost: {cost}. "
                f"For guidance, call DGHS health line: **16401**."
            )
        }

def format_referral_card(urgency: str, lang: str = "en") -> str:
    """Returns a formatted markdown referral recommendation."""
    referral = get_referral(urgency, lang=lang)
    if urgency == URGENCY_EMERGENCY:
        if lang == "bn":
            return f"🚨 **{referral['action_bn']}**\n\n{referral['message_bn']}"
        return f"🚨 **{referral['action']}**\n\n{referral['message_en']}"
    
    if lang == "bn":
        return (
            f"🏥 **সুপারিশকৃত স্বাস্থ্য কেন্দ্র:** {referral['action']}\n\n"
            f"📋 **কখন এই স্বাস্থ্য কেন্দ্রে যাবেন:** {referral.get('when_to_go', '')}\n\n"
            f"💰 **খরচ:** {referral.get('cost', '')}\n\n"
            f"📞 **ডিজিএইচএস হেলথ লাইন:** {referral.get('dghs_hotline', '১৬৪০১')}"
        )
    else:
        return (
            f"🏥 **Recommended facility:** {referral['action']}\n\n"
            f"📋 **When to use this facility:** {referral.get('when_to_go', '')}\n\n"
            f"💰 **Cost:** {referral.get('cost', 'varies')}\n\n"
            f"📞 **DGHS health line:** {referral.get('dghs_hotline', '16401')}"
        )
