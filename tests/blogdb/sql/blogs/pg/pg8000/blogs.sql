-- name: add_many_blogs*!
INSERT INTO blogs (userid, title, content, published)
  VALUES (:userid, :title, :content, :published);
