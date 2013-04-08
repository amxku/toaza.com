/*
 Navicat Premium Data Transfer

 Source Server         : sebug.net
 Source Server Type    : MySQL
 Source Server Version : 50154
 Source Host           : cn.sebug.net
 Source Database       : ginoa

 Target Server Type    : MySQL
 Target Server Version : 50154
 File Encoding         : utf-8

 Date: 04/08/2013 19:22:36 PM
*/

SET NAMES utf8;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
--  Table structure for `article`
-- ----------------------------
DROP TABLE IF EXISTS `article`;
CREATE TABLE `article` (
  `aid` mediumint(9) NOT NULL AUTO_INCREMENT,
  `uid` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `content` text NOT NULL,
  `aptime` int(11) NOT NULL,
  `lastctime` int(11) NOT NULL,
  `comtotal` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`aid`),
  KEY `aid` (`aid`) USING BTREE,
  KEY `uid` (`uid`),
  KEY `lasttcime` (`lastctime`),
  KEY `aptime` (`aptime`),
  KEY `all` (`aid`,`uid`,`title`,`aptime`,`lastctime`,`comtotal`)
) ENGINE=MyISAM AUTO_INCREMENT=148 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `commentreid`
-- ----------------------------
DROP TABLE IF EXISTS `commentreid`;
CREATE TABLE `commentreid` (
  `uid` int(11) NOT NULL,
  `lid` int(11) NOT NULL,
  `atype` enum('0','1') NOT NULL DEFAULT '1',
  `checked` smallint(6) NOT NULL DEFAULT '0',
  `crid` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`crid`,`uid`,`lid`,`atype`),
  KEY `crid` (`uid`,`lid`,`atype`,`crid`,`checked`) USING BTREE,
  KEY `lid` (`lid`),
  KEY `type` (`atype`),
  KEY `check` (`checked`),
  KEY `uid` (`uid`)
) ENGINE=MyISAM AUTO_INCREMENT=19 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `comments`
-- ----------------------------
DROP TABLE IF EXISTS `comments`;
CREATE TABLE `comments` (
  `cid` mediumint(9) NOT NULL AUTO_INCREMENT,
  `uid` int(11) NOT NULL,
  `content` text NOT NULL,
  `cptime` int(11) NOT NULL,
  `aid` int(11) NOT NULL,
  PRIMARY KEY (`cid`),
  KEY `cid` (`cid`,`uid`,`cptime`,`aid`),
  KEY `aid_time` (`cptime`,`aid`),
  KEY `aid` (`aid`)
) ENGINE=MyISAM AUTO_INCREMENT=95 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `logs`
-- ----------------------------
DROP TABLE IF EXISTS `logs`;
CREATE TABLE `logs` (
  `lid` bigint(20) NOT NULL AUTO_INCREMENT,
  `uid` int(11) NOT NULL,
  `optime` int(11) NOT NULL,
  `ipadds` varchar(20) NOT NULL,
  `optype` enum('article','comments','login','setting','avatar','admin','reg','editarticle') NOT NULL,
  `des` varchar(255) DEFAULT NULL,
  `aid` int(11) DEFAULT '0',
  `cid` int(11) DEFAULT '0',
  `nid` int(11) DEFAULT '0',
  `puid` int(11) DEFAULT '0',
  PRIMARY KEY (`lid`,`optype`),
  KEY `all` (`lid`,`uid`,`optime`,`ipadds`,`optype`,`aid`,`cid`) USING BTREE,
  KEY `uid` (`uid`),
  KEY `type_uid_time` (`optype`,`uid`,`optime`),
  KEY `nid` (`nid`),
  KEY `cid` (`cid`),
  KEY `aid` (`aid`)
) ENGINE=MyISAM AUTO_INCREMENT=713 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `node`
-- ----------------------------
DROP TABLE IF EXISTS `node`;
CREATE TABLE `node` (
  `nid` mediumint(9) NOT NULL AUTO_INCREMENT,
  `nName` varchar(50) NOT NULL,
  `nDes` varchar(255) DEFAULT NULL,
  `nCou` int(11) DEFAULT '0',
  `nType` enum('N','C') DEFAULT 'N' COMMENT 'N=node,C=class',
  `subhead` smallint(5) DEFAULT '0',
  `nICO` enum('T','F') DEFAULT 'F',
  `nUrl` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`nid`),
  KEY `nid` (`nid`) USING BTREE,
  KEY `type` (`nType`),
  KEY `shead` (`subhead`),
  KEY `url` (`nUrl`),
  KEY `all` (`nid`,`nName`,`nCou`,`nType`,`nICO`,`nUrl`),
  KEY `ncou` (`nCou`),
  KEY `cou_subh_type` (`nCou`,`nType`,`subhead`)
) ENGINE=MyISAM AUTO_INCREMENT=95 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `noderelated`
-- ----------------------------
DROP TABLE IF EXISTS `noderelated`;
CREATE TABLE `noderelated` (
  `aid` int(9) NOT NULL,
  `nid` int(11) NOT NULL,
  `nrid` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`nrid`,`aid`,`nid`),
  KEY `all` (`aid`,`nid`,`nrid`) USING BTREE,
  KEY `aid` (`aid`) USING HASH,
  KEY `nid` (`nid`) USING HASH,
  KEY `aid_nid` (`aid`,`nid`)
) ENGINE=MyISAM AUTO_INCREMENT=409 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `users`
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `uid` mediumint(9) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `item` text,
  `email` varchar(100) DEFAULT '0',
  `flag` enum('2','1','675') NOT NULL DEFAULT '1',
  `regtime` int(10) NOT NULL,
  `isnofrist` enum('F','T') NOT NULL DEFAULT 'F',
  `isavatar` int(11) NOT NULL DEFAULT '0',
  `sinaid` bigint(11) DEFAULT '0',
  PRIMARY KEY (`uid`),
  KEY `gmailid` (`email`),
  KEY `sinaid` (`sinaid`),
  KEY `username` (`username`) USING BTREE,
  KEY `uid` (`uid`),
  KEY `all` (`uid`,`username`,`email`,`flag`,`regtime`,`isnofrist`,`isavatar`,`sinaid`)
) ENGINE=MyISAM AUTO_INCREMENT=37 DEFAULT CHARSET=utf8;

SET FOREIGN_KEY_CHECKS = 1;
