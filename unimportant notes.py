import git

# Путь к локальному репозиторию
repo_path = '/home/roman-not-hehe/Desktop/sandboxes/pytorch'

# Инициализация объекта репозитория
repo = git.Repo(repo_path)

# Получение списка всех коммитов
commits = repo.iter_commits()

# Пример использования методов и атрибутов коммитов
for commit in commits:
    print("Хеш коммита:", commit.hexsha)
    print("Коммиттер:", commit.committer.name)
    print("Автор:", commit.author.name)
    print("Email автора:", commit.author.email)
    print("Дата автора:", commit.authored_datetime)

    print("Email коммиттера:", commit.committer.email)
    print("Сообщение:", commit.message)
    print("Статистика изменений:", commit.stats)
    print()
