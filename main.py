from datetime import date, timedelta, datetime

import git

start_date = date.today() - timedelta(days=2)
start_date = datetime.combine(start_date, datetime.min.time())


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
        matrix[i][i] = 0
    return matrix


def finder_lonelys(sim_matrix):
    n = len(sim_matrix)
    max_sim = [max(sim_matrix[i]) for i in range(n)]
    print(max_sim)

def main():
    # Путь к локальному репозиторию Git
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
    matrix = create_matrix_of_similarities(author_to_set_of_changed_files, num2author)
    print(matrix)
    for i in range(n):
        for j in range(n):
            print(matrix[i][j], end=" ")
        print()
    finder_lonelys(matrix)


if __name__ == "__main__":
    main()
