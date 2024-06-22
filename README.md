# PlusOne Blog Assignment 

Really cared about creating high quality code that easy to maintain, and i can make it even more abstracted system but i am avoiding over engineering.

[Postman collection](https://app.getpostman.com/join-team?invite_code=11bf1c86f79c924135ceecca0a80f090&target_code=9aa6f2d758c5f2d090497aa48800bcc3)


## Feature

I cared about creating more advanced features than you asked for to make a really usuful product not just assignment want it to finish.

- Blog basic crud operation
- Flags give author more control
  - On/Off commenting on demand
  - Draft the blog to hide it everywhere
  - Public or only for authorized users
- Navigation
  - Full-text search
  - Filter by tag and category
- Interaction on Blog
  - UpVote / DownVote the blog
  - Comment
  - Reply to the comment
- Statistics
  - Visits for the blog


Could add more feature but i want to stuck with the estimation i said, and think this is enough for a functional blog.

## Running it locally

add this to `.env` file

```
DEBUG=0
SECRET_KEY=dee4fd75607d42501de03386b2ce538eda1db5a46a943c094afe1418ab1dc706

DATABASE=postgres
POSTGRES_HOST=db
POSTGRES_PASSWORD=postgres
POSTGRES_USER=postgres
POSTGRES_PORT=5432
POSTGRES_DB=savvy
POSTGRES_SSLMODE=1
```

Then just run docker version

```sh

docker-compose up -d --build

```

then navigate `http://localhost` on port 80 because its running nginx, so make sure this port is not in use

## Deployment instructions

**Not deployed** because my card is declined by heroku
sorry for this step

![card decline](./card.png)

## Why and WhyNot

- Using postgres ?
  - I need full text search
  - it suppor Gin Index so FTS is better performance
  - it automatically store large columns in another storage so reading the row is fast, which is very suitable for the blog system we have
  - MySQL/ Sqlite can't compared to postgres
- Using Gzip middleware ?
  - because blog size may be very long and i want to reduce the response bod size
- don't use Git Branching Strategy ?
  - Because we don't have stable version yet
- Using auth library?
  - My young version wolud create it from scratch but as i grow i realized its better to code little and do more; if there is a stable library well maintained and tested so use it and not reinvent the wheel
