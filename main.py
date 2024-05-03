from datetime import date, timedelta, datetime
import copy
import git
import sys
from colorama import Fore, Style


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


def finder_pseudo_best(sim_matrix):
    n = len(sim_matrix)
    max_sim = [max(sim_matrix[i]) for i in range(n)]
    return max_sim


def re_similarity(sim_matrix_copy, max_sim_copy, set_of_free, set_of_pairs):
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
    n = len(max_sim)
    set_of_pairs = set()
    set_of_free = set(range(n))
    matrix_copy = copy.deepcopy(sim_matrix)
    max_sim_copy = copy.deepcopy(max_sim)
    while max(max_sim_copy) >= 0:
        re_similarity(matrix_copy, max_sim_copy, set_of_free, set_of_pairs)
    return set_of_pairs


def create_list_of_commits(repo_path):
    try:
        days = int(input(Fore.BLUE + Style.BRIGHT + "For how many days back do you want the information?\n"))
        if days <= 0:
            raise ValueError(Fore.RED + "The number of days back must be greater than zero.")
        print(Fore.BLUE + f"You have requested information for the last {days} days")
    except ValueError as e:
        print(Fore.RED + f"Error: {e}")
        print(Fore.RED + "The number of days must be a positive integer number")
        sys.exit(1)
    except Exception as e:
        print(Fore.RED + f"Error: {e}")
        print(Fore.RED + "The number of days must be a positive integer number")
        sys.exit(1)
    start_date = date.today() - timedelta(days=days)
    start_date = datetime.combine(start_date, datetime.min.time())

    repo = git.Repo(repo_path)

    commits = []
    for commit in repo.iter_commits():
        if datetime.combine(commit.authored_datetime, datetime.min.time()) < start_date:
            break
        commits.append(commit)

    if len(commits) == 0:
        print(Fore.RED + f"Please update the git repository. There are no commits in the last {days} days")
        sys.exit(1)
    return commits


def coupling_analysis(author_to_set_of_changed_files, num2author):
    matrix = create_matrix_of_similarities(author_to_set_of_changed_files, num2author)
    maxima_of_columns = finder_pseudo_best(matrix)
    set_of_pairs = greedy_algorithm(matrix, maxima_of_columns)
    sum_of_sim = 0
    flag = str(input(f"Do you want to output zero pairs? yes/no"))
    print(f"Printing pairs of authors and the number of shared files:" + Fore.BLACK)
    list_of_same_files = []
    for pair in set_of_pairs:
        value = matrix[pair[0]][pair[1]]
        sum_of_sim += value
        list_of_same_files.append(value)
        if flag == "no":
            if matrix[pair[0]][pair[1]] > 0:
                print(f"{num2author[pair[0]]:<35}  --  {num2author[pair[1]]:>35}   :   {value}")
        if flag == "yes":
            print(f"{num2author[pair[0]]:<35}  --  {num2author[pair[1]]:>35}   :   {value}")
    print(Fore.BLUE + f"The average \'similarity\' of coupling:" + Fore.BLACK + f" {sum_of_sim / len(set_of_pairs)}")
    list_of_same_files.sort()
    print(
        Fore.BLUE + f"The median \'similarity\' of coupling:" + Fore.BLACK + f" {list_of_same_files[len(list_of_same_files) // 2]}")


def main():
    repo_path = str(input(Fore.BLUE + Style.BRIGHT + f"Please enter the path to your git-repo:\n"))
    # repo_path = '/home/roman-not-hehe/Desktop/sandboxes/pytorch'
    commits = create_list_of_commits(repo_path='/home/roman-not-hehe/Desktop/sandboxes/pytorch')
    author_to_set_of_changed_files = get_changed_files_by_author(commits)
    author2num, num2author = enumerate_authors(commits)
    print(f"Number of commits:" + Fore.BLACK + f" {len(commits)}" + Fore.BLUE + Style.BRIGHT)
    print(f"Number of contributors:" + Fore.BLACK + f" {len(num2author)}" + Fore.BLUE + Style.BRIGHT)
    coupling_analysis(author_to_set_of_changed_files, num2author)
    sys.exit(0)


if __name__ == "__main__":
    main()
