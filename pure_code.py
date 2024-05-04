from datetime import date, timedelta, datetime
import git
import sys
from colorama import Fore, Style


class GitAnalyzer:
    def __init__(self, repo_path):
        self.repo_path = repo_path

    def get_commits_in_last_days(self, days):
        start_date = date.today() - timedelta(days=days)
        start_date = datetime.combine(start_date, datetime.min.time())

        repo = git.Repo(self.repo_path)
        commits = []

        for commit in repo.iter_commits():
            if datetime.combine(commit.authored_datetime, datetime.min.time()) < start_date:
                break
            commits.append(commit)

        if not commits:
            print(Fore.RED + f"Please update the git repository. There are no commits in the last {days} days")
            sys.exit(1)

        return commits


class CommitAnalyzer:
    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def create_matrix_of_similarities(author2set_of_changed_files, number2author):
        n = len(author2set_of_changed_files)
        matrix = [
            [len(author2set_of_changed_files[number2author[i]] & author2set_of_changed_files[number2author[j]]) for i in
             range(n)] for j in range(n)]
        for i in range(n):
            matrix[i][i] = 0
        return matrix


class AnalysisReporter:
    @staticmethod
    def print_changed_files_by_author(changed_files_by_author):
        for author, changed_files in changed_files_by_author.items():
            print(f"author: {author}")
            print("Changed files:")
            for file in changed_files:
                print(file)
            print()

    @staticmethod
    def print_coupling_analysis(set_of_pairs, matrix, num2author):
        sum_of_sim = 0
        flag = str(input(f"Do you want to output zero pairs? yes/no\n"))
        print(f"Printing pairs of authors and the number of shared files:" + Fore.BLACK)
        list_of_same_files = []

        for pair in set_of_pairs:
            value = matrix[pair[0]][pair[1]]
            sum_of_sim += value
            list_of_same_files.append(value)
            if flag == "no":
                if value > 0:
                    print(f"{num2author[pair[0]]:<35}  --  {num2author[pair[1]]:>35}   :   {value}")
            else:
                print(f"{num2author[pair[0]]:<35}  --  {num2author[pair[1]]:>35}   :   {value}")

        print(Fore.BLUE + f"The average 'similarity' of coupling:" + Fore.BLACK + f" {sum_of_sim / len(set_of_pairs)}")
        list_of_same_files.sort()
        print(Fore.BLUE + f"The median 'similarity' of coupling:" + Fore.BLACK + f" {list_of_same_files[len(list_of_same_files) // 2]}")


class GitAnalysisApp:
    def __init__(self):
        self.repo_path = None
        self.days = None

    def get_user_input(self):
        self.repo_path = str(input(Fore.BLUE + Style.BRIGHT + f"Please enter the path to your git-repo:\n"))
        self.days = self.get_valid_days_input()

    def get_valid_days_input(self):
        while True:
            try:
                days = int(input(Fore.BLUE + Style.BRIGHT + "For how many days back do you want the information?\n"))
                if days <= 0:
                    raise ValueError("The number of days back must be greater than zero.")
                print(Fore.BLUE + f"You have requested information for the last {days} days")
                return days
            except ValueError as e:
                print(Fore.RED + f"Error: {e}")
                print(Fore.RED + "The number of days must be a positive integer number")

    def run_analysis(self):
        git_analyzer = GitAnalyzer(self.repo_path)
        commits = git_analyzer.get_commits_in_last_days(self.days)

        changed_files_by_author = CommitAnalyzer.get_changed_files_by_author(commits)
        author2num, num2author = CommitAnalyzer.enumerate_authors(commits)

        print(f"Number of commits:" + Fore.BLACK + f" {len(commits)}" + Fore.BLUE + Style.BRIGHT)
        print(f"Number of contributors:" + Fore.BLACK + f" {len(num2author)}" + Fore.BLUE + Style.BRIGHT)

        matrix = CommitAnalyzer.create_matrix_of_similarities(changed_files_by_author, num2author)
        maxima_of_columns = [max(matrix[i]) for i in range(len(matrix))]
        set_of_pairs = self.greedy_algorithm(matrix, maxima_of_columns)

        AnalysisReporter.print_coupling_analysis(set_of_pairs, matrix, num2author)

    @staticmethod
    def greedy_algorithm(sim_matrix, max_sim):
        n = len(max_sim)
        set_of_pairs = set()
        set_of_free = set(range(n))
        while len(set_of_free) > 0:
            GitAnalysisApp.re_similarity(sim_matrix, set_of_free, set_of_pairs)
        return set_of_pairs

    @staticmethod
    def re_similarity(sim_matrix, set_of_free, set_of_pairs):
        if len(set_of_free) == 1:
            ind = list(set_of_free)[0]
            set_of_pairs.add((ind, ind))
            set_of_free.remove(ind)
        else:
            ind_chosen_1 = list(set_of_free)[0]
            ind_chosen_2 = list(set_of_free)[1]
            max_val = 0
            for ind1 in set_of_free:
                for ind2 in set_of_free:
                    if sim_matrix[ind1][ind2] > max_val:
                        max_val = sim_matrix[ind1][ind2]
                        ind_chosen_1 = ind1
                        ind_chosen_2 = ind2
            set_of_free.remove(ind_chosen_1)
            set_of_free.remove(ind_chosen_2)
            set_of_pairs.add((ind_chosen_1, ind_chosen_2))


def main():
    app = GitAnalysisApp()
    app.get_user_input()
    app.run_analysis()
    sys.exit(0)


if __name__ == "__main__":
    main()
