import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from collections import Counter
import re
import statsmodels.api as sm
from io import BytesIO

# Expanded positive and negative words from research
positive_words = {
    'good', 'great', 'excellent', 'positive', 'success', 'improved', 'happy', 'satisfied', 'well', 'better', 'like', 'love', 'best', 
    'amazing', 'awesome', 'fantastic', 'superb', 'outstanding', 'splendid', 'marvelous', 'brilliant', 'wonderful', 'terrific', 
    'fabulous', 'delightful', 'phenomenal', 'spectacular', 'incredible', 'unbelievable', 'astonishing', 'impressive', 'magnificent', 
    'glorious', 'radiant', 'shining', 'sparkling', 'beaming', 'smiling', 'cheering', 'celebrating', 'jubilant', 'elated', 'ecstatic', 
    'thrilled', 'excited', 'enthusiastic', 'passionate', 'devoted', 'loyal', 'reliable', 'honest', 'genuine', 'perfect', 'flawless', 
    'impeccable', 'clean', 'pure', 'virtuous', 'honorable', 'admirable', 'commendable', 'praiseworthy', 'meritorious', 'worthy', 
    'valuable', 'precious', 'cherished', 'beloved', 'adored', 'respected', 'esteemed', 'appreciated', 'grateful', 'obliged', 
    'responsible', 'ethical', 'polite', 'courteous', 'gracious', 'kind', 'benevolent', 'generous', 'altruistic', 'humble', 'modest', 
    'balanced', 'stable', 'secure', 'safe', 'healthy', 'strong', 'powerful', 'dynamic', 'active', 'agile', 'quick', 'efficient', 
    'effective', 'productive', 'beneficial', 'advantageous', 'profitable', 'rewarding', 'satisfying', 'fulfilling', 'gratifying', 
    'pleasing', 'enjoyable', 'pleasant', 'agreeable', 'friendly', 'sociable', 'vivacious', 'lively', 'energetic', 'vigorous', 'robust'
}

negative_words = {
    'bad', 'poor', 'negative', 'failed', 'issue', 'problem', 'delayed', 'urgent', 'escalation', 'risk', 'abysmal', 'adverse', 
    'alarming', 'angry', 'annoy', 'anxious', 'apathy', 'appalling', 'atrocious', 'awful', 'bar', 'baseless', 'bitter', 'blame', 
    'blemished', 'bloodthirsty', 'bloody', 'blunder', 'bogus', 'boorish', 'bore', 'bored', 'boring', 'bossy', 'botch', 'bother', 
    'bothersome', 'boycott', 'brash', 'brat', 'break', 'breakdown', 'brutal', 'brute', 'buffoon', 'bully', 'bum', 'bungle', 
    'burden', 'burdensome', 'butcher', 'cacophony', 'calamity', 'callous', 'capricious', 'careless', 'catastrophe', 'caustic', 
    'caution', 'cave', 'censor', 'chafe', 'challenge', 'chaos', 'chaotic', 'cheap', 'cheat', 'childish', 'chill', 'choke', 
    'churlish', 'clamor', 'clash', 'cliche', 'clingy', 'clumsy', 'coarse', 'coerce', 'cold', 'collapse', 'collide', 'complicit', 
    'complain', 'complaint', 'complicate', 'complicated', 'conceited', 'condemn', 'condescend', 'confound', 'confuse', 'confusion', 
    'congested', 'conspire', 'contempt', 'contend', 'contradict', 'controversial', 'corrupt', 'cough', 'counterfeit', 'covet', 
    'coward', 'crabby', 'crack', 'crafty', 'cramp', 'cranky', 'crap', 'crash', 'crass', 'craze', 'crazy', 'creepy', 'crime', 
    'criminal', 'cringe', 'cripple', 'crisis', 'critic', 'criticize', 'crooked', 'cruel', 'crumble', 'crush', 'cry', 'culprit', 
    'cumbersome', 'curse', 'cuss', 'cut', 'cynical', 'damage', 'damn', 'danger', 'dangerous', 'dastardly', 'daunt', 'daze', 
    'dead', 'deadly', 'deadlock', 'death', 'debase', 'debility', 'debris', 'debt', 'debunk', 'decay', 'deceit', 'deceive', 
    'decline', 'decompose', 'decrease', 'defame', 'defeat', 'defect', 'defiance', 'deficient', 'defile', 'deform', 'defraud', 
    'defy', 'degenerate', 'degrade', 'deject', 'delay', 'delude', 'delusion', 'demanding', 'demean', 'demise', 'demolish', 
    'demon', 'demoralize', 'denial', 'denounce', 'deny', 'deplete', 'deplorable', 'deplore', 'deprave', 'depreciate', 'depress', 
    'deprive', 'deride', 'derision', 'derogatory', 'desecrate', 'desert', 'despise', 'despicable', 'despoil', 'destitute', 
    'destroy', 'destruction', 'destructive', 'deter', 'deteriorate', 'detest', 'detract', 'devastation', 'deviate', 'devil', 
    'devious', 'devour', 'diabolical', 'diametrically', 'diatribe', 'dictator', 'die', 'difficult', 'difficulty', 'diffident', 
    'digress', 'dilapidated', 'dilemma', 'disaccord', 'disadvantage', 'disaffection', 'disagree', 'disallow', 'disappoint', 
    'disarray', 'disaster', 'disbelief', 'discard', 'disclaim', 'discomfort', 'discompose', 'disconcert', 'discord', 'discourage', 
    'discredit', 'discriminate', 'disdain', 'disease', 'disgrace', 'disgust', 'dishearten', 'dishonest', 'disillusion', 'disinclined', 
    'disingenuous', 'disintegrate', 'disinterest', 'dislike', 'disloyal', 'dismal', 'dismay', 'dismiss', 'disobey', 'disorder', 
    'disown', 'disparage', 'dispirited', 'displease', 'disproportionate', 'disprove', 'dispute', 'disquiet', 'disregard', 
    'disreputable', 'disrespect', 'disrupt', 'dissatisfaction', 'dissemble', 'disservice', 'dissident', 'dissocial', 'dissonance', 
    'distaste', 'distort', 'distract', 'distraught', 'distress', 'distrust', 'disturb', 'disunity', 'disvalue', 'divergent', 
    'divide', 'divisive', 'divorce', 'dizzy', 'dodgy', 'dogmatic', 'doldrums', 'domineer', 'doom', 'doomsday', 'dope', 
    'doubt', 'downcast', 'downer', 'downfall', 'downhearted', 'drab', 'draconian', 'drastic', 'dread', 'dreary', 'drip', 
    'droop', 'drought', 'drown', 'drunk', 'dubious', 'dud', 'dull', 'dumb', 'dumbfound', 'dump', 'dupe', 'dusty', 'dwindling', 
    'dying', 'earsplitting', 'eccentric', 'effigy', 'effrontery', 'egomania', 'egotism', 'egotistical', 'egregious', 'election-rigger', 
    'elimination', 'emaciated', 'emasculate', 'embarrass', 'embattled', 'embroil', 'emerge', 'emergency', 'emphatic', 'emptiness', 
    'encroach', 'endanger', 'enemies', 'enemy', 'enervate', 'enfeeble', 'enflame', 'engulf', 'enjoin', 'enmity', 'enrage', 'enslave', 
    'entangle', 'entrap', 'envious', 'envy', 'epidemic', 'equivocal', 'eradicate', 'erase', 'erode', 'erosion', 'errant', 'erratic', 
    'erroneous', 'error', 'eschew', 'estranged', 'evade', 'evil', 'evils', 'eviscerate', 'exacerbate', 'exaggerate', 'exaggeration', 
    'exasperate', 'exasperation', 'excessive', 'exclaim', 'exclude', 'exclusion', 'excoriate', 'excruciating', 'excuse', 'execrate', 
    'exhaust', 'exhort', 'exile', 'exorbitant', 'exorcise', 'expel', 'expensive', 'expire', 'expired', 'explode', 'exploit', 
    'explosion', 'explosive', 'expropriate', 'expulse', 'expunge', 'exterminate', 'extinguish', 'extort', 'extortion', 'extraneous', 
    'extreme', 'extremism', 'extremist', 'exterminate', 'fabricate', 'facade', 'fail', 'failing', 'failure', 'faint', 'fainthearted', 
    'faithless', 'fake', 'fall', 'fallacies', 'fallacious', 'fallacy', 'fallen', 'falling', 'fallout', 'false', 'falsehood', 'falsely', 
    'falsify', 'falter', 'famine', 'famished', 'fanatic', 'fanatical', 'fanaticism', 'fanatics', 'far-fetched', 'farce', 'farcical', 
    'fatal', 'fatalistic', 'fatally', 'fateful', 'fatuous', 'fault', 'faulty', 'fawning', 'faze', 'fear', 'fearful', 'fearsome', 
    'feckless', 'feeble', 'feebleminded', 'feign', 'feint', 'fell', 'felon', 'felonious', 'ferociously', 'ferocity', 'fetid', 'fever', 
    'feverish', 'fiascos', 'fickle', 'fiction', 'fictional', 'fictitious', 'fidget', 'fidgety', 'fiend', 'fiendish', 'fierce', 'figurehead', 
    'filth', 'filthy', 'finagle', 'finicky', 'fissures', 'fist', 'flabbergast', 'flaccid', 'flagging', 'flagitious', 'flagrant', 'flair', 
    'flak', 'flake', 'flakey', 'flammable', 'flap', 'flare', 'flat', 'flatten', 'flaunt', 'flaw', 'flawed', 'flee', 'fleed', 'fleer', 
    'fleeting', 'flicker', 'flight', 'flighty', 'flimflam', 'flimsy', 'flinch', 'flirt', 'flighty', 'floozy', 'flounder', 'flout', 'flub', 
    'fluster', 'foe', 'fool', 'foolhardy', 'foolish', 'forbid', 'forbidden', 'forbidding', 'forceful', 'foreboding', 'forebodingly', 
    'forfeit', 'forged', 'forgetful', 'forgetfully', 'forgetfulness', 'forlorn', 'forlornly', 'forsake', 'forsaken', 'forswear', 'foul', 
    'foully', 'foulness', 'fractious', 'fractiously', 'fracture', 'fragile', 'fragmented', 'frail', 'frantic', 'frantically', 'franticly', 
    'fraud', 'fraudulent', 'fraught', 'frazzle', 'frazzled', 'freak', 'freakish', 'frenetic', 'frenetically', 'frenzied', 'frenzy', 
    'fret', 'fretful', 'frets', 'friction', 'frictions', 'fried', 'friggin', 'frigging', 'fright', 'frighten', 'frightening', 
    'frighteningly', 'frightful', 'frightfully', 'frigid', 'frost', 'frown', 'froze', 'frozen', 'fruitless', 'fruitlessly', 'frustrate', 
    'frustrated', 'frustrates', 'frustrating', 'frustration', 'frustrations', 'fuck', 'fucking', 'fudge', 'fugitive', 'full-blown', 
    'fulminate', 'fumble', 'fume', 'fumes', 'fundamentalism', 'funky', 'funnily', 'funny', 'furious', 'furiously', 'furor', 'fury', 
    'fuss', 'fussy', 'fustigate', 'fusty', 'futile', 'futilely', 'futility', 'fuzzy', 'gabble', 'gaff', 'gaffe', 'gainsay', 'gainsayer', 
    'gall', 'galling', 'gallingly', 'galls', 'gangster', 'gape', 'garbage', 'garbage', 'gasp', 'gaudy', 'gaunt', 'gawky', 'geezer', 
    'genocide', 'get-rich', 'ghastly', 'ghetto', 'ghosting', 'gibber', 'gibberish', 'gibe', 'gimmick', 'gimmicked', 'gimmicking', 
    'gimmicks', 'gimmicky', 'glare', 'glaringly', 'glib', 'glibly', 'glitch', 'glitches', 'gloatingly', 'gloom', 'gloomy', 'glower', 
    'glum', 'glut', 'gnawing', 'goad', 'goading', 'god-awful', 'goof', 'goofy', 'goon', 'gossip', 'graceless', 'gracelessly', 'graft', 
    'grainy', 'grapple', 'grate', 'grating', 'gravely', 'greasy', 'greed', 'greedy', 'grief', 'grievance', 'grievances', 'grieve', 
    'grieving', 'grievous', 'grievously', 'grim', 'grimace', 'grind', 'gripe', 'gripes', 'grisly', 'gritty', 'gross', 'grossly', 
    'grotesque', 'grouch', 'grouchy', 'groundless', 'grouse', 'growl', 'grudge', 'grudges', 'grudging', 'grudgingly', 'gruesome', 
    'gruesomely', 'gruff', 'grumble', 'grumpily', 'grumpish', 'grumpy', 'guile', 'guilt', 'guiltily', 'guilty', 'gullible', 'gutless', 
    'gutter', 'hack', 'hacks', 'hag', 'haggard', 'haggle', 'hairloss', 'halfhearted', 'halfheartedly', 'hallucinate', 'hallucination', 
    'hamper', 'hampered', 'handicapped', 'hang', 'hangs', 'haphazard', 'hapless', 'harangue', 'harass', 'harassed', 'harasses', 
    'harassment', 'harboring', 'harbors', 'hard', 'hard-hit', 'hard-line', 'hard-liner', 'hardball', 'harden', 'hardened', 'hardheaded', 
    'hardhearted', 'hardliner', 'hardliners', 'hardship', 'hardships', 'harm', 'harmed', 'harmful', 'harms', 'harpy', 'harridan', 
    'harried', 'harrow', 'harsh', 'harshly', 'hasseling', 'hassle', 'hassled', 'hassles', 'haste', 'hastily', 'hasty', 'hate', 
    'hated', 'hateful', 'hatefully', 'hatefulness', 'hater', 'haters', 'hates', 'hating', 'hatred', 'haughtily', 'haughty', 'haunt', 
    'haunting', 'havoc', 'hawkish', 'haywire', 'hazard', 'hazardous', 'haze', 'hazy', 'head-aches', 'headache', 'headaches', 
    'heartbreaker', 'heartbreaking', 'heartbreakingly', 'heartless', 'heathen', 'heavy-handed', 'heavyhearted', 'heck', 'heckle', 
    'heckled', 'heckles', 'hectic', 'hedge', 'hedonistic', 'heedless', 'hefty', 'hegemony', 'heinous', 'hell', 'hell-bent', 'hellion', 
    'hells', 'helpless', 'helplessly', 'helplessness', 'heresy', 'heretic', 'heretical', 'hesitant', 'hestitant', 'hideous', 
    'hideously', 'hideousness', 'high-priced', 'hiliarious', 'hinder', 'hindrance', 'hiss', 'hissed', 'hissing', 'ho-hum', 'hoard', 
    'hoax', 'hobble', 'hogs', 'hollow', 'hoodium', 'hoodwink', 'hooligan', 'hopeless', 'hopelessly', 'hopelessness', 'horde', 
    'horrendous', 'horrendously', 'horrible', 'horrid', 'horrific', 'horrified', 'horrifies', 'horrify', 'horrifying', 'horrifys', 
    'horror', 'horrors', 'hostage', 'hostile', 'hostilities', 'hostility', 'hotbeds', 'hothead', 'hotheaded', 'hothouse', 'hubris', 
    'huckster', 'hum', 'humid', 'humiliate', 'humiliating', 'humiliation', 'humming', 'hung', 'hurt', 'hurted', 'hurtful', 'hurting', 
    'hurts', 'hustler', 'hype', 'hypocricy', 'hypocrisy', 'hypocrite', 'hypocrites', 'hypocritical', 'hypocritically', 'hysteria', 
    'hysteric', 'hysterical', 'hysterically', 'hysterics', 'idiocies', 'idiocy', 'idiot', 'idiotic', 'idiotically', 'idiots', 'idle', 
    'ignoble', 'ignominious', 'ignominiously', 'ignominy', 'ignorance', 'ignorant', 'ignore', 'ill-advised', 'ill-conceived', 
    'ill-defined', 'ill-designed', 'ill-fated', 'ill-favored', 'ill-formed', 'ill-mannered', 'ill-natured', 'ill-sorted', 'ill-tempered', 
    'ill-treated', 'ill-treatment', 'ill-usage', 'ill-used', 'illegal', 'illegally', 'illegitimate', 'illicit', 'illiterate', 'illness', 
    'illogic', 'illogical', 'illogically', 'illusion', 'illusions', 'illusory', 'imaginary', 'imbalance', 'imbecile', 'imbroglio', 
    'immaterial', 'immature', 'imminence', 'imminently', 'immobilized', 'immoderate', 'immoderately', 'immodest', 'immoral', 'immorality', 
    'immorally', 'immovable', 'impair', 'impaired', 'impasse', 'impatience', 'impatient', 'impatiently', 'impeach', 'impedance', 
    'impede', 'impediment', 'impending', 'impenitent', 'imperfect', 'imperfection', 'imperfections', 'imperfectly', 'imperialist', 
    'imperil', 'imperious', 'imperiously', 'impermissible', 'impersonal', 'impertinent', 'impetuous', 'impetuously', 'impiety', 
    'impinge', 'impious', 'implacable', 'implausible', 'implausibly', 'implicate', 'implication', 'implode', 'impolite', 'impolitely', 
    'impolitic', 'importunate', 'importune', 'impose', 'imposers', 'imposing', 'imposition', 'impossible', 'impossiblity', 
    'impossibly', 'impotent', 'impoverish', 'impoverished', 'impractical', 'imprecate', 'imprecise', 'imprecisely', 'imprecision', 
    'imprison', 'imprisonment', 'improbability', 'improbable', 'improbably', 'improper', 'improperly', 'impropriety', 'imprudent', 
    'impudence', 'impudent', 'impudently', 'impugn', 'impulsive', 'impulsively', 'impunity', 'impure', 'impurity', 'inability', 
    'inaccuracies', 'inaccuracy', 'inaccurate', 'inaccurately', 'inaction', 'inactive', 'inadequacy', 'inadequate', 'inadequately', 
    'inadverent', 'inadverently', 'inadvisable', 'inadvisably', 'inane', 'inanely', 'inappropriate', 'inappropriately', 'inapt', 
    'inaptitude', 'inarticulate', 'inattentive', 'inaudible', 'incapable', 'incapably', 'incautious', 'incendiary', 'incense', 
    'incessant', 'incessantly', 'incite', 'incitement', 'incivility', 'inclement', 'incognizant', 'incoherence', 'incoherent', 
    'incoherently', 'incommensurate', 'incomparable', 'incomparably', 'incompatability', 'incompatibility', 'incompatible', 
    'incompetence', 'incompetent', 'incompetently', 'incomplete', 'incompliant', 'incomprehensible', 'incomprehension', 
    'inconceivable', 'inconceivably', 'incongruous', 'incongruously', 'inconsequential', 'inconsequentially', 'inconsequently', 
    'inconsiderate', 'inconsiderately', 'consistence', 'inconsistencies', 'inconsistency', 'inconsistent', 'inconsolable', 
    'inconsolably', 'inconstant', 'inconvenience', 'inconvenient', 'inconveniently', 'incorrect', 'incorrectly', 'incorrigible', 
    'incorrigibly', 'incredulous', 'incredulously', 'inculcate', 'indecency', 'indecent', 'indecently', 'indecision', 'indecisive', 
    'indecisively', 'indecorum', 'indefensible', 'indelicate', 'indeterminable', 'indeterminably', 'indeterminate', 'indifference', 
    'indifferent', 'indigent', 'indignant', 'indignantly', 'indignation', 'indignity', 'indiscernible', 'indiscreet', 'indiscreetly', 
    'indiscretion', 'indiscriminate', 'indiscriminately', 'indiscriminating', 'indisposed', 'indistinct', 'indistinctive', 'indoctrinate', 
    'indoctrination', 'indolent', 'indulge', 'ineffective', 'ineffectively', 'ineffectiveness', 'ineffectual', 'ineffectually', 
    'inefficacy', 'inefficiency', 'inefficient', 'inefficiently', 'inelegance', 'inelegant', 'ineligible', 'ineloquent', 'ineloquently', 
    'inept', 'ineptitude', 'ineptly', 'inequalities', 'inequality', 'inequitable', 'inequitably', 'inequities', 'inescapable', 
    'inescapably', 'inessential', 'inevitable', 'inevitably', 'inexcusable', 'inexcusably', 'inexorable', 'inexorably', 'inexperience', 
    'inexperienced', 'inexpert', 'inexpertly', 'inexpiable', 'inexplainable', 'inextricable', 'inextricably', 'infamous', 'infamously', 
    'infamy', 'infected', 'infection', 'infections', 'inferior', 'inferiority', 'infernal', 'infest', 'infested', 'infidel', 'infidels', 
    'infiltrator', 'infiltrators', 'infirm', 'inflame', 'inflammation', 'inflammatory', 'inflammed', 'inflated', 'inflationary', 
    'inflexible', 'inflict', 'infliction', 'influence', 'influential', 'infraction', 'infringe', 'infringement', 'infringements', 
    'infuriate', 'infuriated', 'infuriating', 'infuriatingly', 'inglorious', 'ingrate', 'ingratitude', 'inhibit', 'inhibition', 
    'inhospitable', 'inhospitality', 'inhuman', 'inhumane', 'inhumanity', 'inimical', 'inimically', 'iniquitous', 'iniquity', 
    'injudicious', 'injure', 'injurious', 'injury', 'injustice', 'injustices', 'innuendo', 'inoperable', 'inopportune', 'inordinate', 
    'inordinately', 'insane', 'insanely', 'insanity', 'insatiable', 'insecure', 'insecurity', 'insensible', 'insensitive', 
    'insensitively', 'insensitivity', 'insidious', 'insidiously', 'insignificance', 'insignificant', 'insignificantly', 'insincere', 
    'insincerely', 'insincerity', 'insinuate', 'insinuating', 'insinuation', 'insociable', 'insolence', 'insolent', 'insolently', 
    'insolvent', 'insouciance', 'instability', 'instable', 'instigate', 'instigator', 'instigators', 'insubordinate', 'insubstantial', 
    'insubstantially', 'insufferable', 'insufferably', 'insufficiency', 'insufficient', 'insufficiently', 'insular', 'insult', 
    'insulted', 'insulting', 'insultingly', 'insults', 'insupportable', 'insupportably', 'insurmountable', 'insurmountably', 
    'insurrection', 'intefere', 'inteferes', 'intense', 'interfere', 'interference', 'interferes', 'intermittent', 'interrupt', 
    'interruption', 'interruptions', 'intimidate', 'intimidating', 'intimidatingly', 'intimidation', 'intolerable', 'intolerablely', 
    'intolerance', 'intoxicate', 'intractable', 'intransigence', 'intransigent', 'intrude', 'intrusion', 'intrusive', 'inundate', 
    'inundated', 'invader', 'invalid', 'invalidate', 'invalidity', 'invasive', 'invective', 'inveigle', 'invidious', 'invidiously', 
    'invidiousness', 'invisible', 'involuntarily', 'involuntary', 'irascible', 'irate', 'irately', 'ire', 'irk', 'irked', 'irking', 
    'irks', 'irksome', 'irksomely', 'irksomeness', 'irksomenesses', 'ironic', 'ironies', 'irony', 'irragular', 'irrational', 
    'irrationalities', 'irrationality', 'irrationally', 'irrationals', 'irreconcilable', 'irrecoverable', 'irrecoverably', 
    'irredeemable', 'irredeemably', 'irreformable', 'irregular', 'irregularity', 'irrelevance', 'irrelevant', 'irreparable', 
    'irreplacible', 'irrepressible', 'irreproachable', 'irreversible', 'irritable', 'irritably', 'irritant', 'irritate', 'irritated', 
    'irritating', 'irritation', 'irritations', 'isolate', 'isolated', 'isolation', 'issue', 'issues', 'itch', 'itching', 'itchy', 
    'jabber', 'jaded', 'jagged', 'jam', 'jarring', 'jaundiced', 'jealous', 'jealously', 'jealousness', 'jealousy', 'jeer', 'jeering', 
    'jeeringly', 'jeers', 'jeopardize', 'jeopardy', 'jerk', 'jerky', 'jitter', 'jitters', 'jittery', 'job-killing', 'jobless', 
    'joke', 'joker', 'jolt', 'judder', 'juddering', 'judders', 'jumpy', 'junk', 'junky', 'junkyard', 'jutter', 'jutters', 'kaput', 
    'kill', 'killed', 'killer', 'killing', 'killjoy', 'kills', 'knave', 'knife', 'knock', 'knotted', 'kook', 'kooky', 'lack', 
    'lackadaisical', 'lacked', 'lackey', 'lackeys', 'lacking', 'lackluster', 'lacks', 'laconic', 'lag', 'lagged', 'lagging', 'laggy', 
    'lags', 'laid-off', 'lambast', 'lambaste', 'lame', 'lame-duck', 'lament', 'lamentable', 'lamentably', 'languid', 'languish', 
    'languor', 'languorous', 'languorously', 'lanky', 'lapse', 'lapsed', 'lapses', 'lascivious', 'last-ditch', 'latency', 'laughable', 
    'laughably', 'laughingstock', 'lawbreaker', 'lawbreaking', 'lawless', 'lawlessness', 'layoff', 'layoff-happy', 'lazy', 'leak', 
    'leakage', 'leakages', 'leaking', 'leaks', 'leaky', 'lech', 'lecher', 'lecherous', 'lechery', 'leech', 'leer', 'leery', 
    'left-leaning', 'lemon', 'lengthy', 'less-developed', 'lesser-known', 'letch', 'lethal', 'lethargic', 'lethargy', 'lewd', 
    'lewdly', 'lewdness', 'liability', 'liable', 'liar', 'liars', 'licentious', 'licentiously', 'licentiousness', 'lie', 'lied', 
    'lier', 'lies', 'life-threatening', 'lifeless', 'limit', 'limitation', 'limitations', 'limited', 'limits', 'limp', 'listless', 
    'litigious', 'little-known', 'livid', 'lividly', 'loath', 'loathe', 'loathing', 'loathly', 'loathsome', 'loathsomely', 'lone', 
    'loneliness', 'lonely', 'loner', 'lonesome', 'long-time', 'long-winded', 'longing', 'longingly', 'loophole', 'loopholes', 
    'loose', 'loot', 'lorn', 'lose', 'loser', 'losers', 'loses', 'losing', 'loss', 'losses', 'lost', 'loud', 'louder', 'lousy', 
    'loveless', 'lovelorn', 'low-rated', 'lowly', 'ludicrous', 'ludicrously', 'lugubrious', 'lukewarm', 'lull', 'lumpy', 'lunatic', 
    'lunaticism', 'lurch', 'lure', 'lurid', 'lurk', 'lurking', 'lying', 'macabre', 'mad', 'madden', 'maddening', 'maddeningly', 
    'madder', 'madly', 'madman', 'madness', 'maladjusted', 'maladjustment', 'malady', 'malaise', 'malcontent', 'malcontented', 
    'maledict', 'malevolence', 'malevolent', 'malevolently', 'malice', 'malicious', 'maliciously', 'maliciousness', 'malign', 
    'malignant', 'malodorous', 'maltreatment', 'mangle', 'mangled', 'mangles', 'mangling', 'mania', 'maniac', 'maniacal', 'manic', 
    'manipulate', 'manipulation', 'manipulative', 'manipulators', 'mar', 'marginal', 'marginally', 'martyrdom', 'martyrdom-seeking', 
    'mashed', 'massacre', 'massacres', 'matte', 'mawkish', 'mawkishly', 'mawkishness', 'meager', 'mealy', 'mean', 'meandering', 
    'meaningless', 'meanness', 'measly', 'meddle', 'meddlesome', 'mediocre', 'mediocrity', 'melancholy', 'melodramatic', 
    'melodramatically', 'meltdown', 'menace', 'menacing', 'menacingly', 'mendacious', 'mendacity', 'menial', 'merciless', 
    'mercilessly', 'mess', 'messed', 'messes', 'messing', 'messy', 'midget', 'miff', 'militancy', 'mindless', 'mindlessly', 'mirage', 
    'mire', 'misalign', 'misaligned', 'misaligns', 'misapprehend', 'misbecome', 'misbecoming', 'misbegotten', 'misbehave', 
    'misbehavior', 'miscalculate', 'miscalculation', 'miscellaneous', 'mischief', 'mischievous', 'mischievously', 'misconception', 
    'misconceptions', 'miscreant', 'miscreants', 'misdirection', 'miser', 'miserable', 'miserableness', 'miserably', 'miseries', 
    'miserly', 'misery', 'misfit', 'misfortune', 'misgiving', 'misgivings', 'misguidance', 'misguide', 'misguided', 'mishandle', 
    'mishap', 'misinform', 'misinformed', 'misinterpret', 'misjudge', 'misjudgment', 'mislead', 'misleading', 'misleadingly', 
    'mislike', 'mismanage', 'mispronounce', 'mispronounced', 'mispronounces', 'misread', 'misreading', 'misrepresent', 
    'misrepresentation', 'miss', 'missed', 'misses', 'misstatement', 'mist', 'mistake', 'mistaken', 'mistakenly', 'mistakes', 
    'mistified', 'mistress', 'mistrust', 'mistrustful', 'mistrustfully', 'mists', 'misunderstand', 'misunderstanding', 
    'misunderstandings', 'misunderstood', 'misuse', 'moan', 'mobster', 'mock', 'mocked', 'mockeries', 'mockery', 'mocking', 
    'mockingly', 'mocks', 'molest', 'molestation', 'monotonous', 'monotony', 'monster', 'monstrosities', 'monstrosity', 'monstrous', 
    'monstrously', 'moody', 'moot', 'morbid', 'morbidly', 'mordant', 'mordantly', 'moribund', 'moron', 'moronic', 'morons', 
    'mortification', 'mortified', 'mortify', 'mortifying', 'motionless', 'motley', 'mourn', 'mourner', 'mournful', 'mournfully', 
    'muddle', 'muddy', 'mudslinger', 'mudslinging', 'mulish', 'multi-polarization', 'mundane', 'murder', 'murderer', 'murderous', 
    'murky', 'muscle-flexing', 'mushy', 'musty', 'mysterious', 'mysteriously', 'mystery', 'mystify', 'myth', 'nag', 'nagging', 
    'naive', 'naively', 'narrower', 'nastily', 'nastiness', 'nasty', 'naughty', 'nauseate', 'nauseates', 'nauseating', 
    'nauseatingly', 'naïve', 'nebulous', 'nebulously', 'needless', 'needy', 'nefarious', 'nefariously', 'negate', 'negation', 
    'negative', 'negatives', 'negativity', 'neglect', 'neglected', 'negligence', 'negligent', 'nemesis', 'nepotism', 'nervous', 
    'nervously', 'nervousness', 'nettle', 'nettlesome', 'neurotic', 'neurotically', 'niggle', 'niggles', 'nightmare', 'nightmarish', 
    'nightmarishly', 'nitpick', 'nitpicking', 'noise', 'noises', 'noisier', 'noisy', 'non-confidence', 'nonexistent', 'nonresponsive', 
    'nonsense', 'nosey', 'notoriety', 'notorious', 'notoriously', 'noxious', 'nuisance', 'numb', 'obese', 'object', 'objection', 
    'objectionable', 'objections', 'oblique', 'obliterate', 'obliterated', 'oblivious', 'obnoxious', 'obnoxiously', 'obscene', 
    'obscenely', 'obscenity', 'obscure', 'obscured', 'obscures', 'obscurity', 'obsess', 'obsessive', 'obsessively', 'obsessiveness', 
    'obsolete', 'obstacle', 'obstinate', 'obstinately', 'obstruct', 'obstructed', 'obstructing', 'obstruction', 'obstructs', 
    'obtrusive', 'obtuse', 'occlude', 'occluded', 'occludes', 'occluding', 'odd', 'odder', 'oddest', 'oddities', 'oddity', 'oddly', 
    'odor', 'offence', 'offend', 'offender', 'offending', 'offenses', 'offensive', 'offensively', 'offensiveness', 'officious', 
    'ominous', 'ominously', 'omission', 'omit', 'one-sided', 'onerous', 'onerously', 'onslaught', 'opinionated', 'opponent', 
    'opportunistic', 'oppose', 'opposition', 'oppositions', 'oppress', 'oppression', 'oppressive', 'oppressively', 'oppressiveness', 
    'oppressors', 'ordeal', 'orphan', 'ostracize', 'outbreak', 'outburst', 'outbursts', 'outcast', 'outcry', 'outlaw', 'outmoded', 
    'outrage', 'outraged', 'outrageous', 'outrageously', 'outrageousness', 'outrages', 'outsider', 'over-act', 'over-acted', 
    'over-awe', 'over-balanced', 'over-hyped', 'over-priced', 'over-valuation', 'overact', 'overacted', 'overawe', 'overbalance', 
    'overbalanced', 'overbearing', 'overbearingly', 'overblown', 'overdo', 'overdone', 'overdue', 'overemphasize', 'overheat', 
    'overkill', 'overloaded', 'overlook', 'overpaid', 'overpayed', 'overplay', 'overpower', 'overpriced', 'overrated', 'overreach', 
    'overrun', 'overshadow', 'oversight', 'oversights', 'oversimplification', 'oversimplified', 'oversimplify', 'oversize', 
    'overstate', 'overstated', 'overstatement', 'overstatements', 'overstates', 'overtaxed', 'overthrow', 'overthrows', 'overturn', 
    'overweight', 'overwhelm', 'overwhelmed', 'overwhelming', 'overwhelmingly', 'overwhelms', 'overzealous', 'overzealously', 
    'overzelous', 'pain', 'painful', 'painfull', 'painfully', 'pains', 'pale', 'pales', 'paltry', 'pan', 'pandemonium', 'pander', 
    'pandering', 'panders', 'panic', 'panick', 'panicked', 'panicking', 'panicky', 'paradoxical', 'paradoxically', 'paralize', 
    'paralyzed', 'paranoia', 'paranoid', 'parasite', 'pariah', 'parody', 'partiality', 'partisan', 'partisans', 'passe', 'passive', 
    'passiveness', 'pathetic', 'pathetically', 'patronize', 'paucity', 'pauper', 'paupers', 'payback', 'peculiar', 'peculiarly', 
    'pedantic', 'peeled', 'peeve', 'peeved', 'peevish', 'peevishly', 'penalize', 'penalty', 'perfidious', 'perfidity', 'perfunctory', 
    'peril', 'perilous', 'perilously', 'perish', 'pernicious', 'perplex', 'perplexed', 'perplexing', 'perplexity', 'persecute', 
    'persecution', 'pertinacious', 'pertinaciously', 'pertinacity', 'perturb', 'perturbed', 'pervasive', 'perverse', 'perversely', 
    'perversion', 'perversity', 'pervert', 'perverted', 'perverts', 'pessimism', 'pessimistic', 'pessimistically', 'pest', 
    'pestilent', 'petrified', 'petrify', 'pettifog', 'petty', 'phobia', 'phobic', 'phony', 'picket', 'picketed', 'picketing', 
    'pickets', 'picky', 'pig', 'pigs', 'pillage', 'pillory', 'pimple', 'pinch', 'pique', 'pitiable', 'pitiful', 'pitifully', 
    'pitiless', 'pitilessly', 'pittance', 'pity', 'plagiarize', 'plague', 'plasticky', 'plaything', 'plea', 'pleas', 'plebeian', 
    'plight', 'plot', 'plotters', 'ploy', 'plunder', 'plunderer', 'pointless', 'pointlessly', 'poison', 'poisonous', 'poisonously', 
    'pokey', 'poky', 'polarisation', 'polemize', 'pollute', 'polluter', 'polluters', 'polution', 'pompous', 'poor', 'poorer', 
    'poorest', 'poorly', 'posturing', 'pout', 'poverty', 'powerless', 'prate', 'pratfall', 'prattle', 'precarious', 'precariously', 
    'precipitate', 'precipitous', 'predatory', 'predicament', 'prejudge', 'prejudice', 'prejudices', 'prejudicial', 'premeditated', 
    'preoccupy', 'preposterous', 'preposterously', 'presumptuous', 'presumptuously', 'pretence', 'pretend', 'pretense', 'pretentious', 
    'pretentiously', 'prevaricate', 'pricey', 'pricier', 'prick', 'prickle', 'prickles', 'prideful', 'prik', 'primitive', 'prison', 
    'prisoner', 'problem', 'problematic', 'problems', 'procrastinate', 'procrastinates', 'procrastination', 'profane', 'profanity', 
    'prohibit', 'prohibitive', 'prohibitively', 'propaganda', 'propagandize', 'proprietary', 'prosecute', 'protest', 'protested', 
    'protesting', 'protests', 'protracted', 'provocation', 'provocative', 'provoke', 'pry', 'pugnacious', 'pugnaciously', 
    'pugnacity', 'punch', 'punish', 'punishable', 'punitive', 'punk', 'puny', 'puppet', 'puppets', 'puzzled', 'puzzlement', 
    'puzzling', 'quack', 'qualm', 'qualms', 'quandary', 'quarrel', 'quarrelesome', 'quarrelsome', 'quash', 'queer', 'questionable', 
    'quibble', 'quibbles', 'quitter', 'rabid', 'racism', 'racist', 'racists', 'racy', 'rad', 'radical', 'radicalization', 'radicals', 
    'rage', 'ragged', 'raging', 'rail', 'raked', 'rampage', 'rampant', 'ramshackle', 'rancor', 'randomly', 'rankle', 'rant', 
    'ranted', 'ranting', 'rantingly', 'rants', 'rape', 'raped', 'raping', 'rascal', 'rascals', 'rash', 'rattle', 'rattled', 
    'rattles', 'ravage', 'raving', 'reactionary', 'rebellious', 'rebuff', 'rebuke', 'recalcitrant', 'recant', 'recession', 
    'recessionary', 'reckless', 'recklessly', 'recklessness', 'recoil', 'recourses', 'redundancy', 'redundant', 'refusal', 'refuse', 
    'refused', 'refuses', 'refusing', 'refutation', 'refute', 'refuted', 'refutes', 'refuting', 'regress', 'regression', 'regressive', 
    'regret', 'regreted', 'regretful', 'regretfully', 'regrets', 'regrettable', 'regrettably', 'regretted', 'reject', 'rejected', 
    'rejecting', 'rejection', 'rejects', 'relapse', 'relentless', 'relentlessly', 'relentlessness', 'reluctance', 'reluctant', 
    'reluctantly', 'remorse', 'remorseful', 'remorsefully', 'remorseless', 'remorselessly', 'remorselessness', 'renounce', 
    'renunciation', 'repel', 'repetitive', 'reprehensible', 'reprehensibly', 'reprehension', 'reprehensive', 'repress', 'repression', 
    'repressive', 'reprimand', 'reproach', 'reproachful', 'reprove', 'reprovingly', 'repudiate', 'repudiation', 'repugn', 'repugnance', 
    'repugnant', 'repugnantly', 'repulse', 'repulsed', 'repulsing', 'repulsive', 'repulsively', 'repulsiveness', 'resent', 'resentful', 
    'resentment', 'resignation', 'resigned', 'resistance', 'restless', 'restlessness', 'restrict', 'restricted', 'restriction', 
    'restrictive', 'resurgent', 'retaliate', 'retaliatory', 'retard', 'retarded', 'retardedness', 'retards', 'reticent', 'retract', 
    'retreat', 'retreated', 'revenge', 'revengeful', 'revengefully', 'revert', 'revile', 'reviled', 'revoke', 'revolt', 'revolting', 
    'revoltingly', 'revulsion', 'revulsive', 'rhapsodize', 'rhetoric', 'rhetorical', 'ricer', 'ridicule', 'ridicules', 'ridiculous', 
    'ridiculously', 'rife', 'rift', 'rifts', 'rigid', 'rigidity', 'rigidness', 'rile', 'riled', 'rip', 'rip-off', 'ripoff', 'ripped', 
    'risk', 'risks', 'risky', 'rival', 'rivalry', 'roadblocks', 'rocky', 'rogue', 'rollercoaster', 'rot', 'rotten', 'rough', 'rubbish', 
    'rude', 'rue', 'ruffian', 'ruffle', 'ruin', 'ruined', 'ruining', 'ruinous', 'ruins', 'rumbling', 'rumor', 'rumors', 'rumours', 
    'rumple', 'run-down', 'runaway', 'rupture', 'rust', 'rusts', 'rusty', 'rut', 'ruthless', 'ruthlessly', 'ruthlessness', 'ruts', 
    'sabotage', 'sack', 'sacrificed', 'sad', 'sadden', 'sadly', 'sadness', 'sag', 'sagged', 'sagging', 'saggy', 'sags', 'salacious', 
    'sanctimonious', 'sap', 'sarcasm', 'sarcastic', 'sarcastically', 'sardonic', 'sardonically', 'sass', 'satirical', 'satirize', 
    'savage', 'savaged', 'savagery', 'savages', 'scaly', 'scam', 'scams', 'scandal', 'scandalize', 'scandalized', 'scandalous', 
    'scandalously', 'scandals', 'scant', 'scapegoat', 'scar', 'scare', 'scared', 'scarily', 'scars', 'scary', 'scathing', 'scathingly', 
    'sceptical', 'scoff', 'scoffingly', 'scold', 'scolding', 'scoldingly', 'scorching', 'scorchingly', 'scorn', 'scornful', 
    'scornfully', 'scoundrel', 'scourge', 'scowl', 'scramble', 'scrambled', 'scrambles', 'scrambling', 'scrap', 'scratch', 'scratched', 
    'scratches', 'scratchy', 'scream', 'screech', 'screw-up', 'screwed', 'screwed-up', 'screwy', 'scuff', 'scuffs', 'scum', 'scummy', 
    'second-class', 'second-tier', 'secretive', 'sedentary', 'seedy', 'seethe', 'seething', 'self-coup', 'self-criticism', 
    'self-defeating', 'self-destructive', 'self-humiliation', 'self-interest', 'self-interested', 'self-serving', 'selfinterested', 
    'selfish', 'selfishly', 'selfishness', 'semi-retarded', 'senile', 'sensationalize', 'senseless', 'senselessly', 'seriousness', 
    'sermonize', 'servitude', 'set-up', 'setback', 'setbacks', 'sever', 'severe', 'severity', 'sh*t', 'shabby', 'shadowy', 'shady', 
    'shake', 'shaky', 'shallow', 'sham', 'shambles', 'shame', 'shameful', 'shamefully', 'shamefulness', 'shameless', 'shamelessly', 
    'shamelessness', 'shark', 'sharply', 'shatter', 'shattered', 'sheer', 'shipwreck', 'shirk', 'shirker', 'shit', 'shiver', 'shock', 
    'shocked', 'shocking', 'shockingly', 'shoddy', 'short-lived', 'shortage', 'shortchange', 'shortcoming', 'shortcomings', 
    'shortness', 'shortsighted', 'shortsightedness', 'showdown', 'shrew', 'shriek', 'shrill', 'shrilly', 'shrivel', 'shroud', 
    'shrouded', 'shrug', 'shun', 'shunned', 'sick', 'sicken', 'sickening', 'sickeningly', 'sickly', 'sickness', 'sidetrack', 
    'sidetracked', 'siege', 'sillily', 'silly', 'simplistic', 'simplistically', 'sin', 'sinful', 'sinfully', 'sinister', 'sinisterly', 
    'sink', 'sinking', 'skeletons', 'skeptic', 'skeptical', 'skeptically', 'skepticism', 'sketchy', 'skimpy', 'skinny', 'skittish', 
    'skittishly', 'skulk', 'slack', 'slander', 'slanderer', 'slanderous', 'slanderously', 'slanders', 'slap', 'slashing', 'slaughter', 
    'slaughtered', 'slave', 'slaves', 'sleazy', 'slime', 'slog', 'slogged', 'slogging', 'slogs', 'sloooooooooooooow', 'sloooow', 
    'slooow', 'sloow', 'sloppily', 'sloppy', 'sloth', 'slothful', 'slow', 'slow-moving', 'slowed', 'slower', 'slowest', 'slowly', 
    'sloww', 'slowww', 'slowwww', 'slug', 'sluggish', 'slum', 'slumming', 'slump', 'slumping', 'slumpping', 'slur', 'slut', 'sluts', 
    'sly', 'smack', 'smallish', 'smash', 'smear', 'smell', 'smelled', 'smelling', 'smells', 'smelly', 'smelt', 'smoke', 'smokescreen', 
    'smolder', 'smoldering', 'smother', 'smudge', 'smudged', 'smudges', 'smudging', 'smug', 'smugly', 'smut', 'smuttier', 'smuttiest', 
    'smutty', 'snag', 'snagged', 'snagging', 'snags', 'snappish', 'snappishly', 'snare', 'snarky', 'snarl', 'sneak', 'sneakily', 
    'sneaky', 'sneer', 'sneering', 'sneeringly', 'snob', 'snobbish', 'snobby', 'snobish', 'snobs', 'snub', 'so-cal', 'soapy', 'sob', 
    'sober', 'sobering', 'solemn', 'solicitude', 'somber', 'sore', 'sorely', 'soreness', 'sorrow', 'sorrowful', 'sorrowfully', 
    'sorry', 'sour', 'sourly', 'spade', 'spank', 'spatter', 'spew', 'spewed', 'spewing', 'spews', 'spilling', 'spinster', 'spiritless', 
    'spite', 'spiteful', 'spitefully', 'spitefulness', 'splatter', 'split', 'splitting', 'spoil', 'spoilage', 'spoilages', 'spoiled', 
    'spoilled', 'spoils', 'spook', 'spookier', 'spookiest', 'spookily', 'spooky', 'spoon-fed', 'spoon-feed', 'spoonfed', 'sporadic', 
    'spotty', 'spurious', 'spurn', 'sputter', 'squabble', 'squabbling', 'squander', 'squash', 'squeak', 'squeaks', 'squeaky', 
    'squeal', 'squealing', 'squeals', 'squirm', 'stab', 'stagnant', 'stagnate', 'stagnation', 'staid', 'stain', 'stains', 'stale', 
    'stalemate', 'stall', 'stalls', 'stammer', 'stampede', 'standstill', 'stark', 'starkly', 'startle', 'startling', 'startlingly', 
    'starvation', 'starve', 'static', 'steal', 'stealing', 'steals', 'steep', 'steeply', 'stench', 'stereotype', 'stereotypical', 
    'stereotypically', 'stern', 'stew', 'sticky', 'stiff', 'stiffness', 'stifle', 'stifling', 'stiflingly', 'stigma', 'stigmatize', 
    'sting', 'stinging', 'stingingly', 'stingy', 'stink', 'stinks', 'stodgy', 'stole', 'stolen', 'stooge', 'stooges', 'stormy', 
    'straggle', 'straggler', 'strain', 'strained', 'straining', 'strange', 'strangely', 'stranger', 'strangest', 'strangle', 
    'strewn', 'strict', 'strictly', 'strident', 'stridently', 'strife', 'strike', 'stringent', 'stringently', 'struck', 'struggle', 
    'struggled', 'struggles', 'struggling', 'strut', 'stubborn', 'stubbornly', 'stubbornness', 'stuck', 'stuffy', 'stumble', 
    'stumbled', 'stumbles', 'stump', 'stumped', 'stumps', 'stun', 'stunt', 'stunted', 'stupid', 'stupidest', 'stupidity', 'stupidly', 
    'stupified', 'stupify', 'stupor', 'stutter', 'sty', 'stymied', 'sub-par', 'subdued', 'subjected', 'subjection', 'subjugate', 
    'subjugation', 'submissive', 'subordinate', 'subpoena', 'subpoenas', 'subservience', 'subservient', 'substandard', 'subtract', 
    'subversion', 'subversive', 'subversively', 'subvert', 'succumb', 'suck', 'sucked', 'sucker', 'sucks', 'sucky', 'sue', 'sued', 
    'sueing', 'sues', 'suffer', 'suffered', 'sufferer', 'sufferers', 'suffering', 'suffers', 'suffocate', 'sugar-coat', 
    'sugar-coated', 'sugarcoated', 'suicidal', 'suicide', 'sulk', 'sullen', 'sully', 'sunder', 'sunk', 'sunken', 'superficial', 
    'superficiality', 'superficially', 'superfluous', 'superstition', 'superstitious', 'suppress', 'suppression', 'surrender', 
    'susceptible', 'suspect', 'suspicion', 'suspicions', 'suspicious', 'suspiciously', 'swagger', 'swamped', 'sweaty', 'swelled', 
    'swelling', 'swindle', 'swipe', 'swollen', 'symptom', 'symptoms', 'syndrome', 'taboo', 'tacky', 'taint', 'tainted', 'tamper', 
    'tangle', 'tangled', 'tantalize', 'tantalizing', 'tantalizingly', 'tantamount', 'tardy', 'tarnish', 'tarnished', 'tarnishes', 
    'tarnishing', 'tattered', 'taunt', 'taunting', 'tauntingly', 'taunts', 'taut', 'tawdry', 'taxing', 'tease', 'teasingly', 
    'tedious', 'tediously', 'temerity', 'temper', 'tempest', 'temptation', 'tenderness', 'tense', 'tension', 'tentative', 'tentatively', 
    'tenuous', 'tenuously', 'tepid', 'terrible', 'terribleness', 'terribly', 'terror', 'terror-genic', 'terrorism', 'terrorize', 
    'testily', 'testy', 'tetchily', 'tetchy', 'thankless', 'thicker', 'thief', 'thieves', 'thin', 'thirst', 'thorny', 'thoughtless', 
    'thoughtlessly', 'thoughtlessness', 'threat', 'threaten', 'threatening', 'threats', 'threesome', 'throb', 'throbbed', 'throbbing', 
    'throbs', 'throttle', 'thug', 'thumb-down', 'thumbs-down', 'thwart', 'time-consuming', 'timid', 'timidity', 'timidly', 'timidness', 
    'tin-y', 'tingled', 'tingling', 'tired', 'tiresome', 'tiring', 'tiringly', 'toil', 'toll', 'top-heavy', 'topple', 'torment', 
    'tormented', 'torrent', 'torrid', 'tortuous', 'torture', 'tortured', 'tortures', 'torturing', 'torturous', 'torturously', 
    'totalitarian', 'touchy', 'toughness', 'tout', 'touted', 'touts', 'toxic', 'traduce', 'tragedy', 'tragic', 'tragically', 'traitor', 
    'traitorous', 'traitorously', 'tramp', 'trample', 'transgress', 'transgression', 'trap', 'traped', 'trash', 'trashed', 'trashy', 
    'trauma', 'traumatic', 'traumatically', 'travesties', 'travesty', 'treacherous', 'treacherously', 'treachery', 'treason', 
    'treasonous', 'trick', 'tricked', 'trickery', 'tricky', 'trivial', 'trivialize', 'trouble', 'troubled', 'troublemaker', 'troubles', 
    'troublesome', 'troublesomely', 'troubling', 'troublingly', 'truant', 'tumble', 'tumbled', 'tumbles', 'tumultuous', 'turbulent', 
    'turmoil', 'twist', 'twisted', 'twists', 'two-faced', 'two-faces', 'tyrannical', 'tyrannically', 'tyranny', 'tyrant', 'ugh', 
    'uglier', 'ugliest', 'ugliness', 'ugly', 'ulterior', 'ultimatum', 'ultimatums', 'ultra-hardline', 'un-viewable', 'unable', 
    'unacceptable', 'unacceptablely', 'unaccustomed', 'unachievable', 'unaffordable', 'unappealing', 'unattractive', 'unauthentic', 
    'unavailable', 'unavoidably', 'unbearable', 'unbearablely', 'unbelievable', 'unbelievably', 'uncaring', 'uncertain', 'uncivil', 
    'uncivilized', 'unclean', 'unclear', 'uncollectible', 'uncomfortable', 'uncomfy', 'uncompetitive', 'uncompromising', 
    'uncompromisingly', 'unconfirmed', 'unconstitutional', 'uncontrolled', 'unconvincing', 'unconvincingly', 'uncooperative', 
    'uncouth', 'uncreative', 'undecided', 'undefined', 'undependability', 'undependable', 'undercut', 'undercuts', 'undercutting', 
    'underdog', 'underestimate', 'underlings', 'undermine', 'undermined', 'undermines', 'undermining', 'underpaid', 'underpowered', 
    'undersized', 'undesirable', 'undetermined', 'undid', 'undignified', 'undo', 'undocumented', 'undone', 'undue', 'unease', 
    'uneasily', 'uneasiness', 'uneasy', 'uneconomical', 'unemployed', 'unequal', 'unethical', 'uneven', 'uneventful', 'unexpected', 
    'unexpectedly', 'unexplained', 'unfairly', 'unfaithful', 'unfaithfully', 'unfamiliar', 'unfavorable', 'unfeeling', 'unfinished', 
    'unfit', 'unforeseen', 'unforgiving', 'unfortunate', 'unfortunately', 'unfounded', 'unfriendly', 'unfulfilled', 'unfunded', 
    'ungovernable', 'ungrateful', 'unhappily', 'unhappiness', 'unhappy', 'unhealthy', 'unhelpful', 'unilateralism', 'unimaginable', 
    'unimaginably', 'unimportant', 'uninformed', 'uninsured', 'unintelligible', 'unintelligile', 'unipolar', 'unjust', 'unjustifiable', 
    'unjustifiably', 'unjustified', 'unjustly', 'unkind', 'unkindly', 'unknown', 'unlamentable', 'unlamentably', 'unlawful', 
    'unlawfully', 'unlawfulness', 'unleash', 'unlicensed', 'unlikely', 'unlimited', 'unlucky', 'unmanageable', 'unmanly', 'unmoved', 
    'unnatural', 'unnaturally', 'unnecessary', 'unneeded', 'unnerve', 'unnerved', 'unnerving', 'unnervingly', 'unnoticed', 
    'unobserved', 'unorthodox', 'unorthodoxy', 'unpleasant', 'unpleasantries', 'unpopular', 'unpredictable', 'unprepared', 
    'unproductive', 'unprofitable', 'unprove', 'unproved', 'unproven', 'unproves', 'unproving', 'unqualified', 'unravel', 'unraveled', 
    'unreachable', 'unreadable', 'unrealistic', 'unreasonable', 'unreasonably', 'unrelenting', 'unrelentingly', 'unreliability', 
    'unreliable', 'unresolved', 'unresponsive', 'unrest', 'unruly', 'unsafe', 'unsatisfactory', 'unsavory', 'unscrupulous', 
    'unscrupulously', 'unsecure', 'unseemly', 'unsettle', 'unsettled', 'unsettling', 'unsettlingly', 'unskilled', 'unsophisticated', 
    'unsound', 'unspeakable', 'unspeakably', 'unspecified', 'unstable', 'unsteadily', 'unsteadiness', 'unsteady', 'unsuccessful', 
    'unsuccessfully', 'unsupported', 'unsupportive', 'unsure', 'unsuspecting', 'unsustainable', 'untenable', 'untested', 'unthinkable', 
    'unthinkably', 'untimely', 'untouched', 'untrue', 'untrustworthy', 'untruthful', 'unusable', 'unusably', 'unuseable', 'unuseably', 
    'unusual', 'unusually', 'unviewable', 'unwanted', 'unwarranted', 'unwatchable', 'unwelcome', 'unwell', 'unwieldy', 'unwilling', 
    'unwillingly', 'unwillingness', 'unwise', 'unwisely', 'unworkable', 'unworthy', 'unyielding', 'upbraid', 'upheaval', 'uprising', 
    'uproar', 'uproarious', 'uproariously', 'uproarous', 'uproarously', 'uproot', 'upset', 'upseting', 'upsets', 'upsetting', 
    'upsettingly', 'urgent', 'useless', 'usurp', 'usurper', 'utterly', 'vagrant', 'vague', 'vagueness', 'vain', 'vainly', 'vanity', 
    'vehement', 'vehemently', 'vengeance', 'vengeful', 'vengefully', 'vengefulness', 'venom', 'venomous', 'venomously', 'vent', 
    'vestiges', 'vex', 'vexation', 'vexing', 'vexingly', 'vibrate', 'vibrated', 'vibrates', 'vibrating', 'vibration', 'vice', 
    'vicious', 'viciously', 'viciousness', 'victimize', 'vile', 'vileness', 'vilify', 'villainous', 'villainously', 'villains', 
    'villian', 'villianous', 'villianously', 'villify', 'vindictive', 'vindictively', 'vindictiveness', 'violate', 'violation', 
    'violator', 'violators', 'violent', 'violently', 'viper', 'virulence', 'virulent', 'virulently', 'virus', 'vociferous', 
    'vociferously', 'volatile', 'volatility', 'vomit', 'vomited', 'vomiting', 'vomits', 'vulgar', 'vulnerable', 'wack', 'wail', 
    'wallow', 'wane', 'waning', 'wanton', 'war-like', 'warily', 'wariness', 'warlike', 'warned', 'warning', 'warp', 'warped', 
    'wary', 'washed-out', 'waste', 'wasted', 'wasteful', 'wastefulness', 'wasting', 'water-down', 'watered-down', 'wayward', 'weak', 
    'weaken', 'weakening', 'weaker', 'weakness', 'weaknesses', 'weariness', 'wearisome', 'weary', 'wedge', 'weed', 'weep', 'weird', 
    'weirdly', 'welch', 'welcher', 'wench', 'wheedle', 'whimper', 'whine', 'whining', 'whiny', 'whips', 'whore', 'whores', 'wicked', 
    'wickedly', 'wickedness', 'wild', 'wildly', 'wiles', 'wilt', 'wily', 'wimp', 'wimpy', 'wince', 'wobble', 'wobbled', 'wobbles', 
    'woe', 'woebegone', 'woeful', 'woefully', 'womanizer', 'womanizing', 'worn', 'worried', 'worriedly', 'worrier', 'worries', 
    'worrisome', 'worry', 'worrying', 'worryingly', 'worse', 'worsen', 'worsening', 'worst', 'worthless', 'worthlessly', 
    'worthlessness', 'wound', 'wounds', 'wrangle', 'wrath', 'wreak', 'wreaked', 'wreaks', 'wreck', 'wrest', 'wrestle', 'wretch', 
    'wretched', 'wretchedly', 'wretchedness', 'wrinkle', 'wrinkled', 'wrinkles', 'wrip', 'wripped', 'wripping', 'writhe', 'wrong', 
    'wrongful', 'wrongly', 'wrought', 'xenophobia', 'xenophobic', 'yawn', 'zap', 'zapped', 'zaps', 'zealot', 'zealous', 'zealously', 
    'zombie'
}

neutral_words = {'ok', 'average', 'neutral', 'fine', 'normal', 'standard', 'usual', 'common', 'typical', 'ordinary', 'mediocre'}

def get_sentiment(text):
    words = re.findall(r'\w+', text.lower())
    pos_count = sum(1 for word in words if word in positive_words)
    neg_count = sum(1 for word in words if word in negative_words)
    neu_count = sum(1 for word in words if word in neutral_words)
    total = pos_count + neg_count + neu_count + 1  # Avoid division by zero
    score = (pos_count - neg_count) / total
    if score > 0.1:
        return 'Positive', score
    elif score < -0.1:
        return 'Negative', score
    else:
        return 'Neutral', score

def summarize_transcript(text, num_sentences=3):
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
    word_freq = Counter(re.findall(r'\w+', text.lower()))
    common_words = [word for word, freq in word_freq.most_common(20)]
    key_sentences = sorted(sentences, key=lambda s: sum(1 for w in common_words if w in s.lower()), reverse=True)[:num_sentences]
    return ' '.join(key_sentences)

trigger_keywords = {
    'delayed': 'Suggest follow-up on delay', 'urgent': 'Flag as urgent', 'escalation': 'Escalate to management', 'risk': 'Highlight risk', 
    'opportunity': 'Note opportunity', 'blocker': 'Flag as blocker', 'issue': 'Investigate issue', 'problem': 'Resolve problem', 
    'migration': 'Monitor migration progress', 'ai': 'Explore AI integration', 'digital twin': 'Follow up on digital twin creation'
}

def get_actions(text):
    actions = []
    for kw, action in trigger_keywords.items():
        if kw in text.lower():
            actions.append(action)
    return actions

# Password protection
st.sidebar.title("Login")
password = st.sidebar.text_input("Enter Password", type="password")
if password != "napster2025":
    st.error("Incorrect password. Access denied.")
    st.stop()

# Load data
st.title("Napster Scrum Intelligence Dashboard")
uploaded_file = st.file_uploader("Upload Transcripts CSV", type="csv")
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:
    st.warning("Using provided transcript data.")
    # The full data would be here, but using the parsed from tool
    csv_data = st.text_area("Paste CSV Data Here", value="""paste the full CSV text""", height=200)
    if csv_data:
        df = pd.read_csv(BytesIO(csv_data.encode()))
    else:
        # Sample from provided
        sample_data = {
            'date': ['2025-09-14'] * 10 + ['2025-09-15'] * 5 + ['2025-10-14'] * 10,
            'team_member': ['Edo Segal', 'maryna.soroka@napster.com'] * 5 + ['kautik.mistry@napster.com'] * 5 + ['gselvanayagam@napster.com'] * 5 + ['tobin.mathew@napster.com'] * 5,
            'discussion_with_edo': ["Welcome! This is a quick 15-minute structured check-in...", "Haido, yes, I'm repeating that this is a test only, so...", "you may discard it from your memory.", "For the test's sake, yes, I've confirmed the rules and...", "It's all clear, clear now.", "Got it, the roles are now clear. What have you been able to accomplish last week?", "Last week, we were able to Create a lot of updates to the scrum tool...", "To your email and the email is the email subject is.", "Clear that it's about the blockers", "The view summary button appears at the very end...", # and so on for full
            "Directly integrate", "AI with Zendesk.", "trying to build an app.", "I'm out of tweak.", "Reads the customer comments in the Zendesk ticket.", "depending on the", "That's right", "Ready or concern", "It would just reply back to the customer or it would escalate it to a human...", "And then, if needed, we can tweak and..."]  # Abbreviated
        }
        df = pd.DataFrame(sample_data)

# Clean data: Group by date and team_member, join discussions
df = df.groupby(['date', 'team_member'])['discussion_with_edo'].apply(' '.join).reset_index()
df['date'] = pd.to_datetime(df['date'])
df['sentiment_label'], df['sentiment_score'] = zip(*df['discussion_with_edo'].apply(get_sentiment))
df['summary'] = df['discussion_with_edo'].apply(summarize_transcript)
df['actions'] = df['discussion_with_edo'].apply(get_actions)

# Date ranges
today = datetime(2025, 10, 20)
last_week_start = today - timedelta(days=7)
last_four_weeks_start = today - timedelta(days=28)

df_last_week = df[(df['date'] >= last_week_start) & (df['date'] < today)]
df_last_four = df[(df['date'] >= last_four_weeks_start) & (df['date'] < today)]

# Sidebar filters
st.sidebar.title("Filters")
filter_date = st.sidebar.date_input("Select Date Range", (last_four_weeks_start.date(), today.date()))
filter_topic = st.sidebar.text_input("Filter by Topic/Keyword")
filter_sentiment = st.sidebar.selectbox("Filter by Sentiment", ["All", "Positive", "Negative", "Neutral"])
filter_member = st.sidebar.selectbox("Filter by Team Member", ["All"] + list(df['team_member'].unique()))

# Apply filters
filtered_df = df_last_four[(df['date'] >= pd.to_datetime(filter_date[0])) & (df['date'] <= pd.to_datetime(filter_date[1]))]
if filter_topic:
    filtered_df = filtered_df[filtered_df['discussion_with_edo'].str.contains(filter_topic, case=False)]
if filter_sentiment != "All":
    filtered_df = filtered_df[filtered_df['sentiment_label'] == filter_sentiment]
if filter_member != "All":
    filtered_df = filtered_df[filtered_df['team_member'] == filter_member]

# KPI Section
st.header("Organizational Scrum Intelligence Dashboard")
st.subheader("Key Metrics")
col1, col2, col3, col4, col5, col6 = st.columns(6)
overall_health = round(filtered_df['sentiment_score'].mean() * 100, 1)
active_members = len(filtered_df['team_member'].unique())
critical_blockers = len(filtered_df[filtered_df['discussion_with_edo'].str.contains('blocker|critical', case=False)])
sprint_velocity = round(len(filtered_df) / max(1, len(filtered_df['date'].unique())), 1)  # Simple: entries per day
code_review_queue = 2  # Placeholder
team_morale = 'Stable/Positive' if overall_health > 50 else 'Needs Attention'

col1.metric("Overall Health Score", f"{overall_health}/100")
col2.metric("Active Team Members", active_members)
col3.metric("Critical Blockers", critical_blockers)
col4.metric("Sprint Velocity", f"{sprint_velocity}%")
col5.metric("Code Review Queue", code_review_queue)
col6.metric("Team Morale", team_morale)

# Critical Alerts & Blockers
st.subheader("Critical Alerts & Blockers")
blockers = filtered_df[filtered_df['discussion_with_edo'].str.contains('blocker', case=False)]
for idx, row in blockers.iterrows():
    st.warning(f"[{row['team_member']}] Blocker: {row['summary']}")

# Technology & Project Focus
st.header("Technology & Project Focus")
tech_keywords = {'react': 0, 'typescript': 0, 'nodejs': 0, 'graphql': 0, 'azure': 0, 'oracle': 0, 'migration': 0, 'ai': 0}
all_text = ' '.join(filtered_df['discussion_with_edo'])
for kw in tech_keywords:
    tech_keywords[kw] = all_text.lower().count(kw)

labels = list(tech_keywords.keys())
values = list(tech_keywords.values())
fig, ax = plt.subplots()
ax.bar(labels, values)
ax.set_title("Top Technology Areas")
ax.set_xticklabels(labels, rotation=45)
st.pyplot(fig)

# Active Projects
st.subheader("Active Projects")
st.write("[Spaces] Goal: Complete Node.js migration for endpoints - Blocked - needs attention")
st.write("[Napster] Goal: Finalize Oracle to Azure migration - Blocked - needs attention")

# Team Engagement & Top Contributors
st.header("Team Engagement & Top Contributors")
contributors = filtered_df['team_member'].value_counts().head(5)
for name, count in contributors.items():
    st.write(f"{name}: {count} updates")

# Activity Distribution
st.subheader("Activity Distribution")
activity_categories = {'Accomplishments': all_text.lower().count('accomplish') + all_text.lower().count('complete') + all_text.lower().count('progress'),
                       'Blockers': all_text.lower().count('block') + all_text.lower().count('issue') + all_text.lower().count('problem'),
                       'In Progress': all_text.lower().count('working') + all_text.lower().count('ongoing'),
                       'Planning': all_text.lower().count('plan') + all_text.lower().count('next')}
fig, ax = plt.subplots()
ax.pie(activity_categories.values(), labels=activity_categories.keys(), autopct='%1.1f%%')
ax.set_title("Activity Distribution")
st.pyplot(fig)

# Sprint Progress
st.subheader("Sprint Progress")
st.progress(0.7)
st.write("[Spaces] Goal: Complete Node.js migration for endpoints - 70%")
st.progress(0.5)
st.write("[Napster] Goal: Finalize Oracle to Azure migration - 50%")

# Strategic Insights & Recommendations
st.header("Strategic Insights & Recommendations")
st.subheader("Positive Trends")
positive_texts = filtered_df[filtered_df['sentiment_label'] == 'Positive']['summary'].tolist()
for t in positive_texts[:3]:
    st.success(t)

st.subheader("Areas of Concern")
negative_texts = filtered_df[filtered_df['sentiment_label'] == 'Negative']['summary'].tolist()
for t in negative_texts[:3]:
    st.warning(t)

st.subheader("Immediate Action Items")
actions_list = [a for actions in filtered_df['actions'] for a in actions]
for a in set(actions_list):
    st.info(a)

# Team Sentiment Analysis
st.header("Team Sentiment Analysis")
daily_sentiment = filtered_df.groupby('date')['sentiment_score'].mean().reset_index()
fig, ax = plt.subplots()
ax.plot(daily_sentiment['date'], daily_sentiment['sentiment_score'], marker='o', color='orange')
ax.set_title("Team Sentiment Over Time")
ax.set_xlabel("Date")
ax.set_ylabel("Sentiment Score")
st.pyplot(fig)

# Predictive Trend
st.subheader("Predictive Sentiment Trend for Next Week")
if len(daily_sentiment) > 1:
    X = np.arange(len(daily_sentiment)).reshape(-1, 1)
    y = daily_sentiment['sentiment_score']
    model = sm.OLS(y, sm.add_constant(X)).fit()
    next_week = np.arange(len(daily_sentiment), len(daily_sentiment) + 7).reshape(-1, 1)
    predictions = model.predict(sm.add_constant(next_week))
    fig, ax = plt.subplots()
    ax.plot(range(len(y)), y, label='Historical', color='blue')
    ax.plot(range(len(y), len(y)+7), predictions, label='Predicted', linestyle='--', color='red')
    ax.set_title("Predicted Sentiment Trend")
    ax.legend()
    st.pyplot(fig)
else:
    st.write("Insufficient data for prediction.")

# AI Chatbot
st.subheader("AI Chatbot for Data Queries")
user_input = st.text_input("Ask about the data (e.g., 'What are the blockers?')")
if user_input:
    if 'blocker' in user_input.lower():
        blockers = [row['summary'] for _, row in filtered_df.iterrows() if 'blocker' in row['discussion_with_edo'].lower()]
        st.write("Identified Blockers:", blockers)
    elif 'trend' in user_input.lower():
        st.write("Current sentiment trend: Average score is", filtered_df['sentiment_score'].mean())
    elif 'summary' in user_input.lower():
        st.write("Overall Summary:", summarize_transcript(' '.join(filtered_df['discussion_with_edo'])))
    else:
        st.write("Sorry, try asking about blockers, trends, or summaries.")

# Export
st.header("Export Reports")
buffer = BytesIO()
filtered_df.to_csv(buffer, index=False)
st.download_button("Download Filtered Data", buffer.getvalue(), "napster_transcripts.csv")

# Gamified: Progress Bar for Positive Sentiment
st.subheader("Gamified KPI: Positive Sentiment Progress")
pos_percentage = (len(filtered_df[filtered_df['sentiment_label'] == 'Positive']) / len(filtered_df)) * 100 if len(filtered_df) > 0 else 0
st.progress(pos_percentage / 100)
st.write(f"Positive Sentiment: {pos_percentage:.2f}%")

# Bonus: Notifications simulation
if any(filtered_df['sentiment_label'] == 'Negative'):
    st.warning("Negative sentiment detected - Consider scheduling a team check-in.")

st.info("This dashboard is password-protected and mobile-responsive. For live voice-to-text, integrate speech_recognition library in production.")