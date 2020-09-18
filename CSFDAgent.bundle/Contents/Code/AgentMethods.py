from Configuration import NAME_PARTITIONING_PERCENTAGE_THRESHOLD, SEARCH_RESULTS_USAGE, TIME_MINUTE_PRECISION, \
    YEAR_PRECISION, TIME_DIFFERENT_PENALTY, RESTRICTED_TYPES
from CSFDScraper2 import parse_search_result, parse_movie

# Mock imports
if 'String' not in globals():
    from Mock import String, HTTP, HTML
    from Mock import Log

CSFD_SEARCH_URL = "http://www.csfd.cz/hledat/?q={}"


def resolve_film_name(full_path, name):
    """
    Resolve name of film from name nad full path

    :param full_path: full path to film
    :type str
    :param name: resolved name from PLEX
    :return:
    """
    if full_path:
        unquoted_full_path = String.Unquote(full_path)

        if 'video_ts' in unquoted_full_path.lower():
            return ''  # TODO: Fix DVD files
        else:
            return name
    else:
        return name


def get_film_metadata(url):
    web_page = HTTP.Request(url).content

    structure = HTML.ElementFromString(web_page)
    metadata = parse_movie(structure)

    return metadata


def film_search(search_string):
    request_url = CSFD_SEARCH_URL.format(String.Quote(search_string))
    web_page = HTTP.Request(request_url).content

    structure = HTML.ElementFromString(web_page)
    search_results = parse_search_result(structure)

    films_metadata = []
    for i, search_result in enumerate(search_results):
        if i >= SEARCH_RESULTS_USAGE:
            return films_metadata

        films_metadata.append(get_film_metadata(search_result.url))

    return films_metadata


def match_film(name, year, duration, metadata):
    if year:
        try:
            if abs(int(year) - int(metadata.year)) > YEAR_PRECISION:
                Log.Debug(metadata.names['CZ'] + 'skipped because of year' + str(year) + ' - ' + str(metadata.year))
                return 0
        except:
            pass

    duration = int(duration)
    best = 0
    penalty = 0

    # Duration
    if duration and metadata.runtime and duration > 0:
        file_duration_min = duration / 60 / 1000

        if abs(file_duration_min - metadata.runtime) > TIME_MINUTE_PRECISION:
            Log.Debug(metadata.names['CZ'] + ' skipped because of duration' + str(file_duration_min) + ' - ' + str(
                metadata.runtime))
            penalty += TIME_DIFFERENT_PENALTY

    # Skip other types
    if metadata.type and String.StripDiacritics(String.Clean(metadata.type)).lower() in RESTRICTED_TYPES:
        return 0

    source_name = String.Clean(name)

    for lang, name in metadata.names.items():
        name = String.Clean(name)
        name = clean_name(name)
        best = max(String.LevenshteinRatio(source_name, name), best)

    return best - penalty


def process_search(search_string, year, duration, score_dictionary, order_dictionary):
    results = film_search(search_string)

    for result in results:
        value = match_film(search_string, year, duration, result)
        if result in score_dictionary:
            if score_dictionary[result] < value:
                score_dictionary[result] = value
                order_dictionary[result] = max(order_dictionary.values()) + 1

        else:
            if value > 0:
                score_dictionary[result] = value
                order_dictionary[result] = max(order_dictionary.values()) + 1

    return score_dictionary, order_dictionary


def shorten_name_forward(name):
    while True:
        if not name:
            return name

        shorter = ' '.join(name.split()[1:])
        separated = name.split()[0]

        try:
            if int(separated) < 10 and int(separated) > 1:
                name = shorter
                continue
            else:
                return shorter
        except:
            return shorter


def shorten_name_backward(name):
    while True:
        if not name:
            return name

        shorter = ' '.join(name.split()[:-1])
        separated = name.split()[-1]

        try:
            if int(separated) < 10 and int(separated) > 1:
                name = shorter
                continue
            else:
                return shorter
        except:
            return shorter


def clean_name(name):
    name = String.Clean(name)
    name = String.StripDiacritics(name)

    chars_replace = '_.\'"!?@#$%^&*()[]{}'
    for char in chars_replace:
        name = name.replace(char, ' ')

    name = name.lower()

    name = name.replace('iii', '3')
    name = name.replace('ii', '2')

    return name


def find_movie(name, year, duration, manual):
    """
    Try to find best film matches based on given metadata

    :param name: Name of the film
    :param year: Year of release
    :param duration: Duration of the film
    :param manual: True if manual search was triggered
    :return: List of best film matches
    """
    name = clean_name(name)
    current_name_forward = name
    current_name_backward = name

    original_name_length = len(name)
    size_threshold = NAME_PARTITIONING_PERCENTAGE_THRESHOLD

    # Cutting of parts of the name to get rid of nonsense text in the name
    score_dictionary = {}
    order_dictionary = {None: 0}
    current_percentage_size_b = 100
    current_percentage_size_f = 100

    while current_percentage_size_b > size_threshold and current_percentage_size_f > size_threshold:
        current_percentage_size_b = 100 * len(current_name_backward) / original_name_length
        current_percentage_size_f = 100 * len(current_name_forward) / original_name_length

        if current_percentage_size_b > size_threshold:
            score_dictionary, order_dictionary = process_search(current_name_backward, year, duration, score_dictionary,
                                                                order_dictionary)
        if current_percentage_size_f > size_threshold:
            score_dictionary, order_dictionary = process_search(current_name_forward, year, duration, score_dictionary,
                                                                order_dictionary)

        current_name_forward = shorten_name_forward(current_name_forward)
        current_name_backward = shorten_name_backward(current_name_backward)

    sorted_results = sorted(score_dictionary.items(), key=lambda x: (x[1], -order_dictionary[x[0]]), reverse=True)

    return sorted_results
