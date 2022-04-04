import spacy
import string
from ..convert_num_to_word import *


def test_convert_num_tok_to_word():
    assert convert_num_tok_to_word("3.5") == "THREE POINT FIVE"
    assert convert_num_tok_to_word("3/5") == "THREE OVER FIVE"
    assert convert_num_tok_to_word("25%") == "TWENTY FIVE PERCENT"
    assert convert_num_tok_to_word("1998") == "NINETEEN NINETY EIGHT"
    assert convert_num_tok_to_word(".5") == "ZERO POINT FIVE"


def test_convert_num_to_word():
    sentences = [
        "IN ISOLATED LUNG VAGAL NEURONS 18.2 59/324 OF THE NEURONS WERE RETROGRADELY LABELED WITH DII THEN 64.4 38/59 PRESENTED TRPV 1 IMMUNOREACTIVITY AMONG THESE DII LABELED NEURONS",
    ]

    references = [
        "IN ISOLATED LUNG VAGAL NEURONS EIGHTEEN POINT TWO FIFTY NINE OVER THREE HUNDRED AND TWENTY FOUR OF THE NEURONS WERE RETROGRADELY LABELED WITH DII THEN SIXTY FOUR POINT FOUR THIRTY EIGHT OVER FIFTY NINE PRESENTED TRPV ONE IMMUNOREACTIVITY AMONG THESE DII LABELED NEURONS"
    ]

    for sent, ref in zip(sentences, references):
        assert convert_num_to_word(sent) == ref


def test_convert_sent_to_word():
    nlp = spacy.load("en_core_web_sm")
    sentences = [
        "Force production at the level of the skeletal myocyte depends on the proper handling of Ca2+ between the sarcoplasmic reticulum and the cytosol.",
        "5 mm tetraethylammonium (TEA; Fluka) was used to partially block potentially present voltage-gated or Ca2+-gated K+ currents, and 100 nm tetrodotoxin (TTX; Sigma-Aldrich) to block potentially present voltage-gated Na+ currents.",
        "p\u2009=\u20090.057, two-tailed t-test n\u2009=\u200914",
        "Downstream signaling effects of shape on nuclear Ca2/MLCK/NFAT 25%.",
        "VSMC were seeded at 10 000 cells per well in 24 well plates or 40 000 cells per well in 6 well plates 24 hours before the start of an experiment.",
        "DM2: Fasting blood glucose >=126 mg/dL or glycated hemoglobin (HbA1c equal or greater than 6.5%).",
        "I was just catching up with you. Many of the cities I checked in and it showed you had already been there 🙂 HaHa! You have now surpassed me….I am only at 32 at this point",
        "Off-Topic Area => General Off-Topic Board => Topic started by: The Poster on December 15, 2005, 08:03 PM",
        "Since there are a total of 4 departments, the total possibilities = 5*3*3*3*3 = 405",
        "Additional information is also available at: http://clinicaltrials.gov/ct2/show/NCT01521546?term=eplerenone&recr=Open&rank=15.",
        "He's there, I'm here.",
        "WIFE AND DAUGHTER IN TO VISIT AND WILL CALL IN A.M",
        "he said  ‘i enjoyed it very much’"
    ]
    references = [
        "FORCE PRODUCTION AT THE LEVEL OF THE SKELETAL MYOCYTE DEPENDS ON THE PROPER HANDLING OF CA TWO PLUS BETWEEN THE SARCOPLASMIC RETICULUM AND THE CYTOSOL",
        "FIVE MM TETRAETHYLAMMONIUM TEA FLUKA WAS USED TO PARTIALLY BLOCK POTENTIALLY PRESENT VOLTAGE GATED OR CA TWO PLUS GATED K CURRENTS AND ONE HUNDRED NM TETRODOTOXIN TTX SIGMA ALDRICH TO BLOCK POTENTIALLY PRESENT VOLTAGE GATED NA CURRENTS",
        "P EQUAL TO ZERO POINT ZERO FIVE SEVEN TWO TAILED T TEST N EQUAL TO FOURTEEN",
        "DOWNSTREAM SIGNALING EFFECTS OF SHAPE ON NUCLEAR CA TWO MLCK NFAT TWENTY FIVE PERCENT",
        "VSMC WERE SEEDED AT TEN THOUSAND CELLS PER WELL IN TWENTY FOUR WELL PLATES OR FORTY THOUSAND CELLS PER WELL IN SIX WELL PLATES TWENTY FOUR HOURS BEFORE THE START OF AN EXPERIMENT",
        "DM TWO FASTING BLOOD GLUCOSE GREATER THAN EQUAL TO ONE HUNDRED AND TWENTY SIX MG DL OR GLYCATED HEMOGLOBIN HBA ONE C EQUAL OR GREATER THAN SIX POINT FIVE PERCENT",
        "I WAS JUST CATCHING UP WITH YOU MANY OF THE CITIES I CHECKED IN AND IT SHOWED YOU HAD ALREADY BEEN THERE HAHA YOU HAVE NOW SURPASSED ME I AM ONLY AT THIRTY TWO AT THIS POINT",
        "OFF TOPIC AREA  GENERAL OFF TOPIC BOARD  TOPIC STARTED BY THE POSTER ON DECEMBER FIFTEEN TWO THOUSAND AND FIVE EIGHT O'CLOCK THREE MINUTES PM",
        "SINCE THERE ARE A TOTAL OF FOUR DEPARTMENTS THE TOTAL POSSIBILITIES EQUAL TO FIVE MULTIPLIED BY THREE MULTIPLIED BY THREE MULTIPLIED BY THREE MULTIPLIED BY THREE EQUAL TO FOUR HUNDRED AND FIVE",
        "ADDITIONAL INFORMATION IS ALSO AVAILABLE AT",
        "HE'S THERE I'M HERE",
        "WIFE AND DAUGHTER IN TO VISIT AND WILL CALL IN AM",
        "HE SAID I ENJOYED IT VERY MUCH"
    ]

    # for sent, ref in zip(sentences, references):
    #     filtered_sent = convert_sent_to_word(sent, nlp)
    #     assert " ".join(filtered_sent) == ref

    for sent, ref in zip(sentences, references):
        filtered_sent = convert_sent_to_word(sent)
        assert " ".join(filtered_sent) == ref
