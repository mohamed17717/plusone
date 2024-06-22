# PlusOne Blog Assignment 

Really cared about creating high quality code that easy to maintain, and i can make it even more abstracted system but i am avoiding over engineering.

I hope you like my way of thinking


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

Just run

```sh

docker-compose up -d --build

```

<!-- then navigate `http://localhost` on port 80 because its running nginx, so make sure this port is not in use -->

## Deployment instructions

**Not deployed yet**

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
