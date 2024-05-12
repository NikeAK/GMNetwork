from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func

from typing import List

from core.database.models import Base, Accounts


class MainDB():
    def __init__(self):
        self.__engine = create_engine('sqlite:///core/database/accounts.db')
        self.__Session = sessionmaker(bind=self.__engine, expire_on_commit=True)
        self.__session = self.__Session()

        Base.metadata.create_all(self.__engine, checkfirst=True)

    def get_accounts(self) -> List[Accounts]:
        accounts = self.__session.query(Accounts).all()
        for account in accounts:
            self.__session.refresh(account)
        return accounts
    
    def get_account_by_id(self, acc_id: int ) -> Accounts:
        account = self.__session.query(Accounts).filter_by(id=acc_id).first()
        self.__session.refresh(account)
        return account

    def add_account(self, acc: Accounts) -> None:
        self.__session.add(acc)
        self.__session.commit()

    def update_account(self, privatekey: str, new_values: dict) -> None:
        stmt = update(Accounts).where(Accounts.privatekey == privatekey).values(new_values)
        self.__session.execute(stmt)
        self.__session.commit()

    def count_accounts(self) -> int:
        return self.__session.query(func.count(Accounts.id)).scalar()

