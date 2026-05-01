--
-- PostgreSQL database dump
--

-- Dumped from database version 17.8 (92d3c18)
-- Dumped by pg_dump version 17.4 (Debian 17.4-1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: admin; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.admin (
    id integer NOT NULL,
    username character varying(120) NOT NULL,
    password_hash character varying(256) NOT NULL,
    email character varying(150),
    created_at timestamp without time zone
);


ALTER TABLE public.admin OWNER TO neondb_owner;

--
-- Name: admin_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.admin_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.admin_id_seq OWNER TO neondb_owner;

--
-- Name: admin_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.admin_id_seq OWNED BY public.admin.id;


--
-- Name: bank; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.bank (
    id integer NOT NULL,
    name character varying(150) NOT NULL,
    code character varying(10)
);


ALTER TABLE public.bank OWNER TO neondb_owner;

--
-- Name: bank_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.bank_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.bank_id_seq OWNER TO neondb_owner;

--
-- Name: bank_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.bank_id_seq OWNED BY public.bank.id;


--
-- Name: biometric_credential; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.biometric_credential (
    id integer NOT NULL,
    referer_id integer NOT NULL,
    credential_id bytea NOT NULL,
    public_key bytea NOT NULL,
    sign_count integer
);


ALTER TABLE public.biometric_credential OWNER TO neondb_owner;

--
-- Name: biometric_credential_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.biometric_credential_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.biometric_credential_id_seq OWNER TO neondb_owner;

--
-- Name: biometric_credential_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.biometric_credential_id_seq OWNED BY public.biometric_credential.id;


--
-- Name: catalog; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.catalog (
    id integer NOT NULL,
    title character varying(100) NOT NULL,
    image_url character varying(255) NOT NULL,
    show_on_home boolean,
    created_at timestamp without time zone,
    description text,
    image character varying(255)
);


ALTER TABLE public.catalog OWNER TO neondb_owner;

--
-- Name: catalog_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.catalog_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.catalog_id_seq OWNER TO neondb_owner;

--
-- Name: catalog_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.catalog_id_seq OWNED BY public.catalog.id;


--
-- Name: coupon; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.coupon (
    id integer NOT NULL,
    code character varying(50) NOT NULL,
    discount_pct double precision NOT NULL,
    is_active boolean,
    created_at timestamp without time zone
);


ALTER TABLE public.coupon OWNER TO neondb_owner;

--
-- Name: coupon_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.coupon_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.coupon_id_seq OWNER TO neondb_owner;

--
-- Name: coupon_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.coupon_id_seq OWNED BY public.coupon.id;


--
-- Name: order; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public."order" (
    id integer NOT NULL,
    reference character varying(100) NOT NULL,
    name character varying(100) NOT NULL,
    email character varying(120) NOT NULL,
    phone character varying(20) NOT NULL,
    terminated boolean,
    amount double precision NOT NULL,
    paid boolean,
    total_amount double precision,
    pickup_code character varying(10),
    pickup_generated_at timestamp without time zone,
    delivered boolean,
    pickup_expired boolean,
    shifted boolean,
    ref_token character varying(100),
    created_at timestamp without time zone
);


ALTER TABLE public."order" OWNER TO neondb_owner;

--
-- Name: order_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.order_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.order_id_seq OWNER TO neondb_owner;

--
-- Name: order_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.order_id_seq OWNED BY public."order".id;


--
-- Name: order_item; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.order_item (
    id integer NOT NULL,
    order_id integer NOT NULL,
    product_id integer NOT NULL,
    quantity double precision NOT NULL,
    unit character varying(20),
    color character varying(50),
    color_name character varying(50),
    color_hex character varying(20),
    collected_quantity double precision,
    created_at timestamp without time zone
);


ALTER TABLE public.order_item OWNER TO neondb_owner;

--
-- Name: order_item_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.order_item_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.order_item_id_seq OWNER TO neondb_owner;

--
-- Name: order_item_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.order_item_id_seq OWNED BY public.order_item.id;


--
-- Name: playing_with_neon; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.playing_with_neon (
    id integer NOT NULL,
    name text NOT NULL,
    value real
);


ALTER TABLE public.playing_with_neon OWNER TO neondb_owner;

--
-- Name: playing_with_neon_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.playing_with_neon_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.playing_with_neon_id_seq OWNER TO neondb_owner;

--
-- Name: playing_with_neon_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.playing_with_neon_id_seq OWNED BY public.playing_with_neon.id;


--
-- Name: product; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.product (
    id integer NOT NULL,
    name character varying(200) NOT NULL,
    description text,
    price integer NOT NULL,
    image character varying(300),
    sold integer,
    delivered integer,
    unit character varying(20),
    product_type character varying(100),
    created_at timestamp without time zone,
    is_active boolean DEFAULT true
);


ALTER TABLE public.product OWNER TO neondb_owner;

--
-- Name: product_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.product_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.product_id_seq OWNER TO neondb_owner;

--
-- Name: product_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.product_id_seq OWNED BY public.product.id;


--
-- Name: rating; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.rating (
    id integer NOT NULL,
    product_id integer,
    order_id integer,
    stars integer,
    comment text,
    created_at timestamp without time zone
);


ALTER TABLE public.rating OWNER TO neondb_owner;

--
-- Name: rating_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.rating_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.rating_id_seq OWNER TO neondb_owner;

--
-- Name: rating_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.rating_id_seq OWNED BY public.rating.id;


--
-- Name: referer; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.referer (
    id integer NOT NULL,
    name character varying(200),
    phone character varying(50),
    email character varying(150),
    whatsapp character varying(50),
    token character varying(64),
    earnings integer,
    referrals_count integer,
    created_at timestamp without time zone,
    status character varying(20),
    bank_id integer,
    bank_name character varying(120),
    account_number character varying(20),
    account_name character varying(120)
);


ALTER TABLE public.referer OWNER TO neondb_owner;

--
-- Name: referer_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.referer_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.referer_id_seq OWNER TO neondb_owner;

--
-- Name: referer_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.referer_id_seq OWNED BY public.referer.id;


--
-- Name: referral_earning; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.referral_earning (
    id integer NOT NULL,
    referer_id integer,
    order_id integer,
    amount double precision,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.referral_earning OWNER TO neondb_owner;

--
-- Name: referral_earning_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.referral_earning_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.referral_earning_id_seq OWNER TO neondb_owner;

--
-- Name: referral_earning_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.referral_earning_id_seq OWNED BY public.referral_earning.id;


--
-- Name: site_settings; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.site_settings (
    id integer NOT NULL,
    hiring_mode boolean
);


ALTER TABLE public.site_settings OWNER TO neondb_owner;

--
-- Name: site_settings_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.site_settings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.site_settings_id_seq OWNER TO neondb_owner;

--
-- Name: site_settings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.site_settings_id_seq OWNED BY public.site_settings.id;


--
-- Name: staffs; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.staffs (
    id integer NOT NULL,
    staff_id character varying(50) NOT NULL,
    name character varying(100) NOT NULL,
    age integer,
    nationality character varying(50),
    state character varying(50),
    lga character varying(50),
    gender character varying(10),
    nin character varying(50),
    email character varying(100),
    username character varying(50),
    password character varying(200),
    role character varying(50),
    bank_name character varying(50),
    bank_code character varying(10),
    account_number character varying(20),
    account_name character varying(100),
    profile_image character varying(200),
    documents text,
    reset_token character varying(255),
    reset_token_expires timestamp without time zone,
    verified boolean,
    verification_status character varying(50),
    rejection_reason character varying(200),
    created_at timestamp without time zone,
    password_hash character varying(256)
);


ALTER TABLE public.staffs OWNER TO neondb_owner;

--
-- Name: staffs_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.staffs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.staffs_id_seq OWNER TO neondb_owner;

--
-- Name: staffs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.staffs_id_seq OWNED BY public.staffs.id;


--
-- Name: subscriber; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.subscriber (
    id integer NOT NULL,
    email character varying(120) NOT NULL,
    opted_in_at timestamp without time zone,
    is_active boolean
);


ALTER TABLE public.subscriber OWNER TO neondb_owner;

--
-- Name: subscriber_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.subscriber_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.subscriber_id_seq OWNER TO neondb_owner;

--
-- Name: subscriber_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.subscriber_id_seq OWNED BY public.subscriber.id;


--
-- Name: tasks; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.tasks (
    id integer NOT NULL,
    title character varying(150) NOT NULL,
    description text,
    status character varying(20),
    created_at timestamp without time zone,
    staff_id integer NOT NULL
);


ALTER TABLE public.tasks OWNER TO neondb_owner;

--
-- Name: tasks_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.tasks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tasks_id_seq OWNER TO neondb_owner;

--
-- Name: tasks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.tasks_id_seq OWNED BY public.tasks.id;


--
-- Name: withdrawal; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.withdrawal (
    id integer NOT NULL,
    referer_id integer,
    amount integer,
    account_details text,
    status character varying(20),
    created_at timestamp without time zone
);


ALTER TABLE public.withdrawal OWNER TO neondb_owner;

--
-- Name: withdrawal_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.withdrawal_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.withdrawal_id_seq OWNER TO neondb_owner;

--
-- Name: withdrawal_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.withdrawal_id_seq OWNED BY public.withdrawal.id;


--
-- Name: admin id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.admin ALTER COLUMN id SET DEFAULT nextval('public.admin_id_seq'::regclass);


--
-- Name: bank id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.bank ALTER COLUMN id SET DEFAULT nextval('public.bank_id_seq'::regclass);


--
-- Name: biometric_credential id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.biometric_credential ALTER COLUMN id SET DEFAULT nextval('public.biometric_credential_id_seq'::regclass);


--
-- Name: catalog id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.catalog ALTER COLUMN id SET DEFAULT nextval('public.catalog_id_seq'::regclass);


--
-- Name: coupon id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.coupon ALTER COLUMN id SET DEFAULT nextval('public.coupon_id_seq'::regclass);


--
-- Name: order id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public."order" ALTER COLUMN id SET DEFAULT nextval('public.order_id_seq'::regclass);


--
-- Name: order_item id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.order_item ALTER COLUMN id SET DEFAULT nextval('public.order_item_id_seq'::regclass);


--
-- Name: playing_with_neon id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.playing_with_neon ALTER COLUMN id SET DEFAULT nextval('public.playing_with_neon_id_seq'::regclass);


--
-- Name: product id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.product ALTER COLUMN id SET DEFAULT nextval('public.product_id_seq'::regclass);


--
-- Name: rating id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.rating ALTER COLUMN id SET DEFAULT nextval('public.rating_id_seq'::regclass);


--
-- Name: referer id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.referer ALTER COLUMN id SET DEFAULT nextval('public.referer_id_seq'::regclass);


--
-- Name: referral_earning id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.referral_earning ALTER COLUMN id SET DEFAULT nextval('public.referral_earning_id_seq'::regclass);


--
-- Name: site_settings id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.site_settings ALTER COLUMN id SET DEFAULT nextval('public.site_settings_id_seq'::regclass);


--
-- Name: staffs id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.staffs ALTER COLUMN id SET DEFAULT nextval('public.staffs_id_seq'::regclass);


--
-- Name: subscriber id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.subscriber ALTER COLUMN id SET DEFAULT nextval('public.subscriber_id_seq'::regclass);


--
-- Name: tasks id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.tasks ALTER COLUMN id SET DEFAULT nextval('public.tasks_id_seq'::regclass);


--
-- Name: withdrawal id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.withdrawal ALTER COLUMN id SET DEFAULT nextval('public.withdrawal_id_seq'::regclass);


--
-- Data for Name: admin; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.admin (id, username, password_hash, email, created_at) FROM stdin;
1	admin	scrypt:32768:8:1$AfftmDS0U91BO1tO$197dedd77fb745620587468b4c3e94b46a6123bc21d0a8587cd9b5626972aa88df97c8cb6517edb6aa425b5ce9f745dbc1dd4dff1c0f5d91084747a40bb9b138	admin@test.com	2026-04-09 11:54:13.060346
\.


--
-- Data for Name: bank; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.bank (id, name, code) FROM stdin;
1	Opay	100004
\.


--
-- Data for Name: biometric_credential; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.biometric_credential (id, referer_id, credential_id, public_key, sign_count) FROM stdin;
1	15	\\x01bf91cbb0a189ce6fb470a3261095f0bee1870c95c6db2820e12ccd1c5ab62cfac09d1fd6efceae7aade558f56713543dd4955d3d59b70d27ae9e0358fbcfc1d2	\\xa5010203262001215820be5db757f1e28d018aae029009a8893e04a3deeb0a60250f23735c269d25dc1c22582033c26fcbdce1a7a7c00c1c039b5001beda4e33c97b8b4cbb1f86689cacb08b81	0
2	15	\\x017b59e538340d6f9495aa1b0250888b511ee206269cdff93d3fb11aa73b1d9aa9f45c7c9d890c55eb919f1e198c23e6a87e95271027a62ff8a29b8bc759f133dc	\\xa5010203262001215820470cbb1b57d036fda878a6cd9fa804b637b1e430b1aa79cd89d180300678f50e225820f5d1ff56f390f99aa1b8d61ebc931de6c387192bcc6cae3990329ef9b3ccb3f9	0
4	13	\\x01e33ec7480de540f96c0479bcb5d2db5b25f736189956a42007fc893ad125b36162db9ad347f50536a573ff64bcc2c247937d21ccd7155bab1c63787a39a4bc10	\\xa501020326200121582077eb81d48c148ebe8cf0905a8c720f00279cae3af336c41bd3dd63762f7ee74f225820a4ebcbd1bba4b37949b6b38ccbdf03f2441b3db3f04ce822a437d2c413f3ba1e	0
\.


--
-- Data for Name: catalog; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.catalog (id, title, image_url, show_on_home, created_at, description, image) FROM stdin;
1	Interior Painting	https://res.cloudinary.com/dqt3iwm6z/image/upload/v1776695754/heavenly_catalog/pzffqdejer3eki8sa5a0.jpg	t	2026-04-20 14:35:54.763131	This project was handles by Heavenly Paint Limited Team at Ibesikpo area...\r\n\r\nPaint used was Acrylic Finish	https://res.cloudinary.com/dqt3iwm6z/image/upload/v1776695754/heavenly_catalog/pzffqdejer3eki8sa5a0.jpg
\.


--
-- Data for Name: coupon; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.coupon (id, code, discount_pct, is_active, created_at) FROM stdin;
4	TESTSALESHPL	5	t	2026-04-20 18:06:14.359623
\.


--
-- Data for Name: order; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public."order" (id, reference, name, email, phone, terminated, amount, paid, total_amount, pickup_code, pickup_generated_at, delivered, pickup_expired, shifted, ref_token, created_at) FROM stdin;
11	9ea08cd2157c44a1ba5ed513ce24a00a	Mikpidogho Edet	mikpidoghoedet@gmail.com	08122889225	f	100	t	\N	ZXIWPAY	2026-04-20 08:53:11.932825	t	f	f	\N	2026-04-20 08:51:44.805723
14	d8450df641ab410391026c0abbdab203	Mikpidogho Edet	mikpidoghoedet@gmail.com	08122889225	f	140550	t	\N	ACVFSTC	2026-04-22 14:05:52.987238	t	f	f	4d68180a78b04e418ac9f879cd91ff26	2026-04-22 14:02:43.552118
16	HP-04357A4	Tera			f	7795000	t	\N	WK-D30D7AC	\N	t	t	f	\N	2026-04-23 08:24:43.248132
17	HP-4EA90D0	Treasure			f	120000	t	\N	WK-2048E4F	\N	t	t	f	\N	2026-04-24 17:14:33.376974
\.


--
-- Data for Name: order_item; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.order_item (id, order_id, product_id, quantity, unit, color, color_name, color_hex, collected_quantity, created_at) FROM stdin;
4	11	12	1	buckets	\N	White	\N	1	2026-04-20 08:53:12.217286
6	14	10	3	buckets	\N	White	\N	3	2026-04-22 14:05:53.274075
7	16	5	50	buckets	\N		#ffffff	50	2026-04-23 08:24:43.955706
8	17	1	1	buckets	\N		#ffffff	1	2026-04-24 17:14:34.042927
\.


--
-- Data for Name: playing_with_neon; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.playing_with_neon (id, name, value) FROM stdin;
1	c4ca4238a0	0.18290262
2	c81e728d9d	0.684571
3	eccbc87e4b	0.84222597
4	a87ff679a2	0.040357776
5	e4da3b7fbb	0.06984456
6	1679091c5a	0.5597726
7	8f14e45fce	0.3610975
8	c9f0f895fb	0.7744664
9	45c48cce2e	0.15738681
10	d3d9446802	0.09893388
11	c4ca4238a0	0.979883
12	c81e728d9d	0.70708823
13	eccbc87e4b	0.21050449
14	a87ff679a2	0.17699409
15	e4da3b7fbb	0.038695037
16	1679091c5a	0.12322425
17	8f14e45fce	0.7519898
18	c9f0f895fb	0.5969979
19	45c48cce2e	0.5766002
20	d3d9446802	0.47398084
21	c4ca4238a0	0.490939
22	c81e728d9d	0.5893527
23	eccbc87e4b	0.92539436
24	a87ff679a2	0.95778304
25	e4da3b7fbb	0.18415746
26	1679091c5a	0.04551823
27	8f14e45fce	0.3385319
28	c9f0f895fb	0.012066436
29	45c48cce2e	0.45351723
30	d3d9446802	0.37414977
31	c4ca4238a0	0.9296603
32	c81e728d9d	0.6708336
33	eccbc87e4b	0.091920935
34	a87ff679a2	0.94260687
35	e4da3b7fbb	0.6753217
36	1679091c5a	0.23069458
37	8f14e45fce	0.07599897
38	c9f0f895fb	0.4167191
39	45c48cce2e	0.7524919
40	d3d9446802	0.9382037
\.


--
-- Data for Name: product; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.product (id, name, description, price, image, sold, delivered, unit, product_type, created_at, is_active) FROM stdin;
4	Textcoat Paint 	Textcoat Paint is a high-performance textured coating designed to give walls a decorative, rough-pattern finish while providing strong surface protection. Unlike smooth paints, it contains special aggregates that create depth and texture, making it ideal for both aesthetic enhancement and practical durability.\r\n\r\nIt is widely used for exterior walls, fences, and feature surfaces where a bold, stylish appearance is desired. The textured nature of Textcoat Paint helps to effectively conceal cracks, uneven surfaces, and minor wall imperfections, delivering a more refined and uniform look.\r\n\r\nFormulated for toughness, Textcoat Paint is highly resistant to weather conditions such as rain, heat, and moisture. It forms a durable protective layer that extends the lifespan of surfaces while maintaining its appearance over time.\r\n\r\nEasy to apply using rollers or spray techniques, it offers flexibility in creating different patterns and designs to suit modern architectural styles. With its combination of strength, texture, and visual appeal, Textcoat Paint is an excellent choice for customers seeking both decoration and long-lasting protection in one solution.	19000	https://res.cloudinary.com/dqt3iwm6z/image/upload/v1776353065/tmkha5eslodrqvddtuun.jpg	0	0	pcs	\N	2026-04-11 19:14:42.230925	t
2	Standard Emulsion Paint 	Standard Emulsion Paint is a cost-effective interior wall coating designed to provide a clean, smooth, and uniform finish for everyday spaces. It is ideal for ceilings, low-traffic areas, and general-purpose applications where affordability and decent coverage are key priorities. This type of paint offers a matte appearance that helps to hide minor wall imperfections while giving walls a neat and refreshed look.\r\nFormulated for easy application, Standard Emulsion Paint spreads smoothly and dries quickly, making it suitable for both new projects and repainting jobs. It delivers good coverage with minimal effort and is available in a wide range of colors to suit different styles and preferences.\r\nWhile not as durable or washable as premium finishes like silk or satin, Standard Emulsion Paint remains a reliable choice for achieving simple, attractive results at a budget-friendly cost. It is perfect for customers looking for an economical solution without compromising basic quality.	17000	https://res.cloudinary.com/dqt3iwm6z/image/upload/v1776353136/rhdpphm1vvoylrh9gzex.jpg	0	0	pcs	\N	2026-04-09 20:56:43.728198	t
3	Acrylic Finish 	Acrylic Finish Paint is a high-quality coating formulated with advanced acrylic resins to deliver superior durability, smooth appearance, and long-lasting color performance.\r\n\r\n It provides a refined finish that can range from matte to semi-gloss, making it suitable for both interior and exterior applications where strength and beauty are essential.\r\n\r\nKnown for its excellent adhesion and flexibility, Acrylic Finish Paint forms a strong bond with surfaces, allowing it to withstand temperature changes without cracking or peeling. \r\n\r\nIt dries quickly and creates a tough, water-resistant layer that protects walls from moisture, stains, and everyday wear. \r\n\r\nThis type of paint also offers outstanding color retention, resisting fading caused by sunlight and harsh weather conditions, making it ideal for exterior walls and high-traffic interior areas. \r\n\r\nIts smooth application and high coverage ensure a neat, professional finish with fewer coats required.\r\n\r\nWith its combination of durability, weather resistance, and elegant finish, Acrylic Finish Paint is a reliable choice for customers seeking a modern, long-lasting solution for both residential and commercial spaces.	60000	https://res.cloudinary.com/dqt3iwm6z/image/upload/v1776351372/d0k5ctd0pg1hzppdieex.jpg	1	1	pcs	\N	2026-04-10 18:55:18.633641	t
8	Standard Matte Emulsion	Matte Emulsion Paint is a smooth, non-reflective interior coating designed to give walls a soft, elegant, and modern appearance. It provides a flat finish with little to no shine, making it ideal for creating a calm and sophisticated atmosphere in living rooms, bedrooms, and ceilings.\r\n\r\nOne of its key advantages is its ability to effectively hide surface imperfections such as cracks, bumps, and uneven textures, delivering a clean and uniform look even on older walls. Its velvety finish absorbs light rather than reflecting it, enhancing color depth and giving walls a rich, subtle appearance.\r\n\r\n\r\nMatte Emulsion Paint is easy to apply and dries quickly, offering good coverage with a smooth, consistent result. However, it is best suited for low-traffic areas, as it is less durable and not as washable as higher-sheen finishes like silk or satin.\r\n\r\nWith its refined appearance and excellent coverage, Matte Emulsion Paint is an ideal choice for customers seeking a simple, stylish, and cost-effective finish that prioritizes beauty over heavy-duty performance.	28150	https://res.cloudinary.com/dqt3iwm6z/image/upload/v1776353269/spfzwtbeswh24yeiyl8u.jpg	0	0	pcs	\N	2026-04-11 19:36:01.524413	t
7	Acrylic Emulsion Paint 	Acrylic Emulsion Paint is a high-performance water-based coating formulated with acrylic polymer binders to provide superior durability, flexibility, and long-lasting color. It delivers a smooth, attractive finish while combining the ease of emulsion paints with the enhanced strength of acrylic technology.\r\n\r\nThis type of paint is known for its excellent adhesion and fast-drying properties, allowing it to form a tough, protective film that resists cracking, peeling, and fading over time. Once dry, it becomes water-resistant, making it suitable for both interior and exterior surfaces exposed to varying weather conditions. \r\n\r\nAcrylic Emulsion Paint also offers good washability and stain resistance, making it ideal for high-traffic areas such as living rooms, hallways, and commercial spaces. Its low odour and environmentally friendly composition make it comfortable for indoor use while maintaining strong performance outdoors.\r\n\r\nWith its balance of durability, weather resistance, and smooth decorative finish, Acrylic Emulsion Paint is an excellent choice for customers seeking a reliable and long-lasting solution for modern building surfaces.	17999	https://res.cloudinary.com/dqt3iwm6z/image/upload/v1776353220/yehy30ko4sva8g8r9iad.jpg	0	0	pcs	\N	2026-04-11 19:33:16.226264	t
6	Superior Emulsion Paint 	Superior Emulsion Paint is a high-grade interior coating designed to deliver enhanced durability, smooth finish, and long-lasting beauty compared to standard emulsion paints. It provides a rich matte appearance that gives walls a clean, elegant look while maintaining excellent coverage and color uniformity.\r\n\r\nFormulated with quality acrylic or polymer binders, Superior Emulsion Paint offers strong adhesion and improved resistance to moisture, stains, and everyday wear. It spreads easily and dries quickly, forming a durable protective layer that helps walls stay fresh and attractive over time.\r\n\r\nThis paint is ideal for interior walls, ceilings, and plastered surfaces in homes, offices, and commercial spaces. Its low-odour and washable properties make it suitable for modern living environments where cleanliness and comfort are important.\r\n\r\nWith its balance of affordability, durability, and improved performance, Superior Emulsion Paint is a perfect choice for customers seeking a higher-quality finish than standard emulsion without moving fully into premium paint categories.	18999	https://res.cloudinary.com/dqt3iwm6z/image/upload/v1776353373/n8bfvulsspbkmhujx7at.jpg	0	0	pcs	\N	2026-04-11 19:29:53.730533	t
9	Flexcoat Paint 	Flexcoat Paint is a high-performance elastic coating designed to provide superior waterproofing, flexibility, and long-lasting protection for walls and exterior surfaces. It is specially formulated with advanced acrylic or polymer resins to create a durable, flexible film that moves with the surface, preventing cracks and structural damage over time.\r\n\r\nUnlike conventional paints, Flexcoat Paint forms a waterproof barrier that protects walls from rain, moisture, and environmental damage while still allowing the surface to “breathe,” preventing trapped moisture and peeling . \r\nIts elasticity enables it to bridge hairline cracks and adapt to slight building movements without losing its protective properties .\r\n\r\nFlexcoat Paint offers excellent adhesion to surfaces such as concrete, plaster, and masonry, making it ideal for exterior walls, façades, and areas exposed to harsh weather conditions. It is also resistant to UV rays, ensuring long-lasting color and performance even under intense sunlight.\r\n\r\nEasy to apply and highly durable, Flexcoat Paint is an ideal choice for customers seeking a reliable solution that combines decoration with advanced protection, especially for buildings that require strong resistance against water penetration and surface cracking.	16985	https://res.cloudinary.com/dqt3iwm6z/image/upload/v1776353184/gmjvxv0mqwig3pmu5yhi.jpg	0	0	pcs	\N	2026-04-11 19:38:58.428747	t
1	Silk/ Satin  Finish	Silk Finish Paint is a premium interior coating designed to deliver a smooth, soft-sheen appearance that enhances the beauty of any space. It provides a luxurious finish that sits between matte and gloss, offering a subtle shine that reflects light gently while maintaining an elegant look. Ideal for living rooms, bedrooms, and hallways, this paint type not only elevates the aesthetic appeal of walls but also adds a layer of durability.\r\nFormulated for excellent coverage and long-lasting performance, Silk Finish Paint is easy to apply and dries to a flawless, even surface. Its washable and stain-resistant properties make it perfect for areas with moderate traffic, allowing walls to stay clean and fresh with minimal maintenance. The finish resists marks, scuffs, and mild moisture, ensuring your walls retain their beauty over time.\r\nWith its rich color retention and smooth texture, Silk Finish Paint brings both style and practicality together, making it a perfect choice for modern interiors that demand both elegance and resilience.	120000	https://res.cloudinary.com/dqt3iwm6z/image/upload/v1776353332/w6yhui4e5xodsovxoev1.jpg	1	1	pcs	\N	2026-04-09 12:19:25.887197	t
12	Filler	This is used to fill up cracks on the walls before painting 	100	https://res.cloudinary.com/dqt3iwm6z/image/upload/v1776675025/chaefc1lrmkpnnajulfx.png	1	0	pcs	\N	2026-04-20 08:50:26.74462	f
5	Nylon Paint	Nylon Paint is a specialized high-performance coating formulated with nylon (polyamide) resins to deliver exceptional strength, flexibility, and resistance to wear. It produces a smooth, slightly glossy finish that is both protective and functional, making it suitable for surfaces exposed to heavy use or harsh conditions.\r\n\r\nDesigned for durability, Nylon Paint offers outstanding resistance to abrasion, impact, chemicals, and moisture, forming a tough protective layer that helps extend the lifespan of coated surfaces. It adheres strongly and maintains its integrity even under stress, making it ideal for industrial, metal, and high-contact applications. \r\n\r\nThis type of paint is also valued for its flexibility and resistance to cracking or peeling, allowing it to perform well under temperature changes and mechanical movement. Its smooth surface finish helps reduce friction and can provide additional benefits such as corrosion protection and easy cleaning.\r\n\r\nWith its combination of strength, resilience, and protective qualities, Nylon Paint is a reliable choice for customers seeking a durable coating solution for demanding environments where ordinary paints may not perform effectively.	155900	https://res.cloudinary.com/dqt3iwm6z/image/upload/v1776353462/rboeys3dts7cnax27xsp.jpg	50	50	pcs	\N	2026-04-11 19:23:30.435273	t
10	Matte (acrylic) 	Matte Paint is a low-sheen finish typically formulated with acrylic resins, combining the durability of acrylic paint with a smooth, non-reflective appearance. It delivers a flat, elegant look while still offering better strength and adhesion than basic emulsion paints.\r\n\r\nUnlike standard matte emulsions, Acrylic Matte Paint provides improved washability, moisture resistance, and longer-lasting color, making it suitable for both interior and light exterior applications. It forms a breathable yet protective coating that resists mild stains and everyday wear without developing shine.\r\n\r\nIts smooth, even coverage helps to hide minor surface imperfections while maintaining a modern, soft-touch finish. The paint applies easily, dries quickly, and retains its color without fading, even under moderate environmental exposure.\r\n\r\nWith its balance of durability and refined appearance, Matte Paint is an ideal choice for customers who want a clean, non-gloss finish without sacrificing performance and longevity.	48850	https://res.cloudinary.com/dqt3iwm6z/image/upload/v1776353301/wj8rlmsmdffhaiwemy9q.jpg	3	0	pcs	\N	2026-04-15 16:59:59.852476	t
\.


--
-- Data for Name: rating; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.rating (id, product_id, order_id, stars, comment, created_at) FROM stdin;
1	1	\N	5	Great	2026-04-09 20:48:55.489315
2	10	\N	5	This is the best paint I have used so far 	2026-04-16 15:59:18.251237
3	10	\N	5		2026-04-16 16:11:59.529089
4	10	\N	5		2026-04-16 16:15:35.403698
\.


--
-- Data for Name: referer; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.referer (id, name, phone, email, whatsapp, token, earnings, referrals_count, created_at, status, bank_id, bank_name, account_number, account_name) FROM stdin;
17	Wisdom Lawrence Sampson 	\N	wisdomlawrence2001@gmail.com	09011543102 	39c88ca9fbdc4d209e21572d760f0657	0	0	2026-04-23 07:19:33.979287	approved	1	Opay	9011543102	Wisdom Lawrence Sampson
18	Wisdom Lawrence Sampson 	\N	wisdomlawrence2001@gmail.com	09011543102	5ad26d22f2814220a1c8280dbefd000b	0	0	2026-04-23 07:21:56.817927	approved	1	Opay	9011543102	Wisdom Lawrence Sampson
5	Okpo Isaiah Anthony 	\N	\N	2349168147858	500efe78ac5d4afc8263fd7fc48c5550	0	0	2026-04-14 18:46:22.202862	approved	\N	Opay	9168147858	Okpo Isaiah Anthony
12	Favour Ubon Marcel	\N	favourmarcel06@gmail.com	2348129638839	bec1e487319b4ae9840c5a3d4e72c56f	0	0	2026-04-17 09:15:00.726738	approved	\N	First City Monument Bank (FCMB)	1036815142	Favour Ubon Marcel
13	Ete ete antigha bassey	\N	enobassey564@gmail.com	8144339624	5833379405734b92970949716781dc6c	0	0	2026-04-18 20:40:04.200811	approved	\N	Zenith Bank	2388532281	Ete ete antigha bassey
15	Mikpidogho Emmanuel Edet 	\N	mikpidoghoedet@gmail.com	2348122889225	4d68180a78b04e418ac9f879cd91ff26	9838	0	2026-04-22 12:35:01.366604	approved	1	Opay	8122889225	Mikpidogho Emmanuel Edet
\.


--
-- Data for Name: referral_earning; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.referral_earning (id, referer_id, order_id, amount, "timestamp") FROM stdin;
\.


--
-- Data for Name: site_settings; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.site_settings (id, hiring_mode) FROM stdin;
1	f
\.


--
-- Data for Name: staffs; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.staffs (id, staff_id, name, age, nationality, state, lga, gender, nin, email, username, password, role, bank_name, bank_code, account_number, account_name, profile_image, documents, reset_token, reset_token_expires, verified, verification_status, rejection_reason, created_at, password_hash) FROM stdin;
3	HPL1776363901	Mikpidogho Edet	26	Nigeria	Akwa Ibom	Uyo	Male	49375371167	mikpidoghoedet@gmail.com	Heavenlyboy	scrypt:32768:8:1$jFBM5UfNI7M7s9zE$bb88184e6e52a02df7cf1c52daf87e04fdb6cea5f8f53c0c6f655941b52750654427a56a28e70ba96a872275f5dacb32d38ab51853289f2eafcfe41ab08023dc	Manager	Opay	999992	8122889225	Mikpidogho Emmanuel Edet	https://res.cloudinary.com/dqt3iwm6z/image/upload/v1776364802/staff_profiles/kydseyrt0ocpp1g0b5dp.jpg	https://res.cloudinary.com/dqt3iwm6z/image/upload/v1776363899/staff_documents/q1amhjeewzaf9dzzpcq8.jpg,https://res.cloudinary.com/dqt3iwm6z/raw/upload/v1776363900/staff_documents/oumgplqldc8iwwk1sqmc,https://res.cloudinary.com/dqt3iwm6z/raw/upload/v1776363900/staff_documents/i9imxlds0dwrsoppckry,documents/TIN_cert.pdf,documents/manual_work.docx,documents/AILiteracy.docx	\N	\N	t	approved	No files was found in your upload. Try uploading new ones 	2026-04-16 18:25:01.971175	\N
2	HPL1776174864	Favour Marcel	19	Nigeria	Akwa Ibom	Uyo	Female	60540157500	favourmarcel06@gmail.com	FavyTara	scrypt:32768:8:1$owsWDMz3s7cIj8JE$cc3e647769c5fd95eb936fef9a08d9c2c78c7f1835235d2e0f4fd675812d1d460c3c7bb8a4abbe710e7a826f3e2c077a10016b5a77cf050a3ba16c4a7b3b3e5d	Secretary	First City Monument Bank	213523	1036815142	Marcel Favour Ubon 	https://res.cloudinary.com/dqt3iwm6z/image/upload/v1776416890/staff_profiles/jtrnlmvdqphyi5olxq2y.jpg	documents/1759007493183.jpg	\N	\N	t	approved	\N	2026-04-14 13:54:25.101541	\N
\.


--
-- Data for Name: subscriber; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.subscriber (id, email, opted_in_at, is_active) FROM stdin;
1	mikpidoghoedet@gmail.com	2026-04-16 17:53:43.453179	t
2	favourmarcel06@gmail.com	2026-04-18 21:38:02.54273	t
\.


--
-- Data for Name: tasks; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.tasks (id, title, description, status, created_at, staff_id) FROM stdin;
2	Creating complementary card	Create a complementary card and send for me 	Pending	2026-04-14 14:05:38.120149	2
\.


--
-- Data for Name: withdrawal; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.withdrawal (id, referer_id, amount, account_details, status, created_at) FROM stdin;
\.


--
-- Name: admin_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.admin_id_seq', 1, true);


--
-- Name: bank_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.bank_id_seq', 1, true);


--
-- Name: biometric_credential_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.biometric_credential_id_seq', 4, true);


--
-- Name: catalog_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.catalog_id_seq', 1, true);


--
-- Name: coupon_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.coupon_id_seq', 4, true);


--
-- Name: order_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.order_id_seq', 17, true);


--
-- Name: order_item_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.order_item_id_seq', 8, true);


--
-- Name: playing_with_neon_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.playing_with_neon_id_seq', 40, true);


--
-- Name: product_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.product_id_seq', 12, true);


--
-- Name: rating_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.rating_id_seq', 4, true);


--
-- Name: referer_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.referer_id_seq', 18, true);


--
-- Name: referral_earning_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.referral_earning_id_seq', 1, false);


--
-- Name: site_settings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.site_settings_id_seq', 1, true);


--
-- Name: staffs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.staffs_id_seq', 3, true);


--
-- Name: subscriber_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.subscriber_id_seq', 2, true);


--
-- Name: tasks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.tasks_id_seq', 2, true);


--
-- Name: withdrawal_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.withdrawal_id_seq', 1, false);


--
-- Name: admin admin_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.admin
    ADD CONSTRAINT admin_pkey PRIMARY KEY (id);


--
-- Name: admin admin_username_key; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.admin
    ADD CONSTRAINT admin_username_key UNIQUE (username);


--
-- Name: bank bank_name_key; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.bank
    ADD CONSTRAINT bank_name_key UNIQUE (name);


--
-- Name: bank bank_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.bank
    ADD CONSTRAINT bank_pkey PRIMARY KEY (id);


--
-- Name: biometric_credential biometric_credential_credential_id_key; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.biometric_credential
    ADD CONSTRAINT biometric_credential_credential_id_key UNIQUE (credential_id);


--
-- Name: biometric_credential biometric_credential_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.biometric_credential
    ADD CONSTRAINT biometric_credential_pkey PRIMARY KEY (id);


--
-- Name: catalog catalog_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.catalog
    ADD CONSTRAINT catalog_pkey PRIMARY KEY (id);


--
-- Name: coupon coupon_code_key; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.coupon
    ADD CONSTRAINT coupon_code_key UNIQUE (code);


--
-- Name: coupon coupon_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.coupon
    ADD CONSTRAINT coupon_pkey PRIMARY KEY (id);


--
-- Name: order_item order_item_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.order_item
    ADD CONSTRAINT order_item_pkey PRIMARY KEY (id);


--
-- Name: order order_pickup_code_key; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public."order"
    ADD CONSTRAINT order_pickup_code_key UNIQUE (pickup_code);


--
-- Name: order order_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public."order"
    ADD CONSTRAINT order_pkey PRIMARY KEY (id);


--
-- Name: order order_reference_key; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public."order"
    ADD CONSTRAINT order_reference_key UNIQUE (reference);


--
-- Name: playing_with_neon playing_with_neon_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.playing_with_neon
    ADD CONSTRAINT playing_with_neon_pkey PRIMARY KEY (id);


--
-- Name: product product_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.product
    ADD CONSTRAINT product_pkey PRIMARY KEY (id);


--
-- Name: rating rating_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.rating
    ADD CONSTRAINT rating_pkey PRIMARY KEY (id);


--
-- Name: referer referer_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.referer
    ADD CONSTRAINT referer_pkey PRIMARY KEY (id);


--
-- Name: referer referer_token_key; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.referer
    ADD CONSTRAINT referer_token_key UNIQUE (token);


--
-- Name: referral_earning referral_earning_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.referral_earning
    ADD CONSTRAINT referral_earning_pkey PRIMARY KEY (id);


--
-- Name: site_settings site_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.site_settings
    ADD CONSTRAINT site_settings_pkey PRIMARY KEY (id);


--
-- Name: staffs staffs_email_key; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.staffs
    ADD CONSTRAINT staffs_email_key UNIQUE (email);


--
-- Name: staffs staffs_nin_key; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.staffs
    ADD CONSTRAINT staffs_nin_key UNIQUE (nin);


--
-- Name: staffs staffs_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.staffs
    ADD CONSTRAINT staffs_pkey PRIMARY KEY (id);


--
-- Name: staffs staffs_staff_id_key; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.staffs
    ADD CONSTRAINT staffs_staff_id_key UNIQUE (staff_id);


--
-- Name: staffs staffs_username_key; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.staffs
    ADD CONSTRAINT staffs_username_key UNIQUE (username);


--
-- Name: subscriber subscriber_email_key; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.subscriber
    ADD CONSTRAINT subscriber_email_key UNIQUE (email);


--
-- Name: subscriber subscriber_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.subscriber
    ADD CONSTRAINT subscriber_pkey PRIMARY KEY (id);


--
-- Name: tasks tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_pkey PRIMARY KEY (id);


--
-- Name: withdrawal withdrawal_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.withdrawal
    ADD CONSTRAINT withdrawal_pkey PRIMARY KEY (id);


--
-- Name: biometric_credential biometric_credential_referer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.biometric_credential
    ADD CONSTRAINT biometric_credential_referer_id_fkey FOREIGN KEY (referer_id) REFERENCES public.referer(id);


--
-- Name: order_item order_item_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.order_item
    ADD CONSTRAINT order_item_order_id_fkey FOREIGN KEY (order_id) REFERENCES public."order"(id);


--
-- Name: order_item order_item_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.order_item
    ADD CONSTRAINT order_item_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.product(id);


--
-- Name: rating rating_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.rating
    ADD CONSTRAINT rating_order_id_fkey FOREIGN KEY (order_id) REFERENCES public."order"(id);


--
-- Name: rating rating_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.rating
    ADD CONSTRAINT rating_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.product(id);


--
-- Name: referer referer_bank_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.referer
    ADD CONSTRAINT referer_bank_id_fkey FOREIGN KEY (bank_id) REFERENCES public.bank(id);


--
-- Name: referral_earning referral_earning_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.referral_earning
    ADD CONSTRAINT referral_earning_order_id_fkey FOREIGN KEY (order_id) REFERENCES public."order"(id);


--
-- Name: referral_earning referral_earning_referer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.referral_earning
    ADD CONSTRAINT referral_earning_referer_id_fkey FOREIGN KEY (referer_id) REFERENCES public.referer(id);


--
-- Name: tasks tasks_staff_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_staff_id_fkey FOREIGN KEY (staff_id) REFERENCES public.staffs(id);


--
-- Name: withdrawal withdrawal_referer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.withdrawal
    ADD CONSTRAINT withdrawal_referer_id_fkey FOREIGN KEY (referer_id) REFERENCES public.referer(id);


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: public; Owner: cloud_admin
--

ALTER DEFAULT PRIVILEGES FOR ROLE cloud_admin IN SCHEMA public GRANT ALL ON SEQUENCES TO neon_superuser WITH GRANT OPTION;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: cloud_admin
--

ALTER DEFAULT PRIVILEGES FOR ROLE cloud_admin IN SCHEMA public GRANT ALL ON TABLES TO neon_superuser WITH GRANT OPTION;


--
-- PostgreSQL database dump complete
--

