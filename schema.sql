DROP TABLE IF EXISTS pemesanan;
DROP TABLE IF EXISTS pembayaran;
DROP TABLE IF EXISTS admins;
DROP TABLE IF EXISTS pemesanan_items;
DROP TABLE IF EXISTS barang;


CREATE TABLE pemesanan (
id CHAR(16) NOT NULL PRIMARY KEY,
full_name TEXT NOT NULL,
address VARCHAR(50) NOT NULL,
email VARCHAR(30) NOT NULL,
phone_number VARCHAR(15) NOT NULL,
description TEXT,
created_at TIMESTAMP NOT NULL);

CREATE TABLE pembayaran (
id CHAR(12) NOT NULL PRIMARY KEY,
total BIGINT NOT NULL,
paid BIGINT NOT NULL,
created_at TIMESTAMP NOT NULL,
pemesanan CHAR(16) NOT NULL);

CREATE TABLE admins (
id NUMERIC(6) NOT NULL PRIMARY KEY,
nama VARCHAR(50) NOT NULL,
email VARCHAR(50) NOT NULL,
username VARCHAR(30) NOT NULL,
password CHAR(128) NOT NULL);

CREATE TABLE pemesanan_items (
pemesanan CHAR(16) NOT NULL,
total BIGINT NOT NULL,
description TEXT,
price BIGINT NOT NULL,
status BOOLEAN NOT NULL DEFAULT 'false',
barang CHAR(12) NOT NULL);

CREATE TABLE barang (
id CHAR(12) NOT NULL PRIMARY KEY,
name VARCHAR(100) NOT NULL,
description TEXT,
price BIGINT NOT NULL,
status BOOLEAN NOT NULL DEFAULT 'true');

ALTER TABLE pembayaran ADD CONSTRAINT pembayaran_pemesanan_pemesanan_id FOREIGN KEY (pemesanan) REFERENCES pemesanan(id) ON DELETE CASCADE ON UPDATE NO ACTION;
ALTER TABLE pemesanan_items ADD CONSTRAINT pemesanan_items_pemesanan_pemesanan_id FOREIGN KEY (pemesanan) REFERENCES pemesanan(id) ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE pemesanan_items ADD CONSTRAINT pemesanan_items_barang_barang_id FOREIGN KEY (barang) REFERENCES barang(id) ON DELETE NO ACTION ON UPDATE NO ACTION;