from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass

class Accounts(Base):
    __tablename__ = 'accounts'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    address: Mapped[str] = mapped_column(nullable=True)
    privatekey: Mapped[str]
    proxy: Mapped[str]

    id_gm: Mapped[str] = mapped_column(nullable=True)
    checkin: Mapped[int] = mapped_column(default=86401)
    balance: Mapped[int] = mapped_column(nullable=True)

    email: Mapped[str] = mapped_column(nullable=True)
    invite_code: Mapped[str] = mapped_column(nullable=True)
    
    agent_id: Mapped[int] = mapped_column(nullable=True)
    agent_nft_id: Mapped[int] = mapped_column(nullable=True)
    agent_token_id: Mapped[int] = mapped_column(nullable=True)
    agent_name: Mapped[str] = mapped_column(nullable=True)
    agent_description: Mapped[str] = mapped_column(nullable=True)
    agent_image: Mapped[str] = mapped_column(nullable=True)
    agent_rarity: Mapped[int] = mapped_column(nullable=True)
    agent_energy: Mapped[int] = mapped_column(nullable=True)

    boost: Mapped[int] = mapped_column(nullable=True)
    level: Mapped[int] = mapped_column(nullable=True)
    
