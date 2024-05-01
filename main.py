from datetime import date, timedelta, datetime
import copy
import git

start_date = date.today() - timedelta(days=15)
start_date = datetime.combine(start_date, datetime.min.time())
set_of_free = set()
set_of_pairs = set()


def get_changed_files_by_author(commits):
    changed_files_by_author = {}
    for commit in commits:
        author_name = commit.author.name
        changed_files = commit.stats.files.keys()
        if author_name not in changed_files_by_author:
            changed_files_by_author[author_name] = set(changed_files)
        else:
            changed_files_by_author[author_name].update(changed_files)
    return changed_files_by_author


def enumerate_authors(commits):
    author_to_number = {}
    number_to_author = {}
    authors_set = set()
    numb = 0
    for commit in commits:
        if commit.author.name in authors_set:
            continue
        authors_set.add(commit.author.name)
        author_to_number[commit.author.name] = numb
        number_to_author[numb] = commit.author.name
        numb += 1
    return author_to_number, number_to_author


def print_changed_files_by_author(commits):
    changed_files_by_author = get_changed_files_by_author(commits)
    for author, changed_files in changed_files_by_author.items():
        print(f"author: {author}")
        print("Changed files:")
        for file in changed_files:
            print(file)
        print()


def create_matrix_of_similarities(author2set_of_changed_files, number2author):
    n = len(author2set_of_changed_files)
    matrix = [
        [len(author2set_of_changed_files[number2author[i]] & author2set_of_changed_files[number2author[j]]) for i in
         range(n)] for j in range(n)]
    for i in range(n):
        matrix[i][i] = -1
    return matrix


def finder_lonelys(sim_matrix):
    n = len(sim_matrix)
    max_sim = [max(sim_matrix[i]) for i in range(n)]
    return max_sim


def re_similarity(sim_matrix_copy, max_sim_copy):
    global set_of_free, set_of_pairs
    if len(set_of_free) == 1:
        ind, val = max(enumerate(max_sim_copy), key=lambda x: x[1])
        set_of_pairs.add((ind, ind))
        max_sim_copy[ind] = -1
    else:
        n = len(sim_matrix_copy)
        ind1, val = max(enumerate(max_sim_copy), key=lambda x: x[1])
        ind2, val = max(enumerate(sim_matrix_copy[ind1]), key=lambda x: x[1])
        set_of_free.remove(ind1)
        set_of_free.remove(ind2)
        set_of_pairs.add((ind1, ind2))
        for i in range(n):
            sim_matrix_copy[i][ind1] = -1
            sim_matrix_copy[i][ind2] = -1
        max_sim_copy[ind1] = -1
        max_sim_copy[ind2] = -1


def greedy_algorithm(sim_matrix, max_sim):
    global set_of_free
    n = len(max_sim)
    set_of_free = set(range(n))
    matrix_copy = copy.deepcopy(sim_matrix)
    max_sim_copy = copy.deepcopy(max_sim)
    while max(max_sim_copy) >= 0:
        re_similarity(matrix_copy, max_sim_copy)


def main():
    repo_path = '/home/roman-not-hehe/Desktop/sandboxes/pytorch'
    repo = git.Repo(repo_path)
    commits = []
    for commit in repo.iter_commits():
        if datetime.combine(commit.authored_datetime, datetime.min.time()) < start_date:
            break
        commits.append(commit)
    author_to_set_of_changed_files = get_changed_files_by_author(commits)
    print("done changed files")
    author2num, num2author = enumerate_authors(commits)
    print("done enumerate authors")
    n = len(num2author)
    print(n)
    matrix = create_matrix_of_similarities(author_to_set_of_changed_files, num2author)
    lili = finder_lonelys(matrix)
    greedy_algorithm(matrix, lili)
    print(set_of_pairs)
    sum = 0
    for pair in set_of_pairs:
        sum += matrix[pair[0]][pair[1]]
        print(num2author[pair[0]], " -- ", num2author[pair[1]], "  :  ", matrix[pair[0]][pair[1]])
    print(sum / len(set_of_pairs))


if __name__ == "__main__":
    main()
