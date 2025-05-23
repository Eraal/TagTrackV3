PGDMP  0                    }         
   tagtrackv3    17.5    17.5 B    �           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                           false                        0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                           false                       0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                           false                       1262    25106 
   tagtrackv3    DATABASE     �   CREATE DATABASE tagtrackv3 WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'English_United States.1252';
    DROP DATABASE tagtrackv3;
                     postgres    false            �            1259    25108    admins    TABLE     Z  CREATE TABLE public.admins (
    id integer NOT NULL,
    username character varying(50) NOT NULL,
    password character varying(255) NOT NULL,
    email character varying(100),
    full_name character varying(100),
    "position" character varying(100),
    last_login timestamp without time zone,
    created_at timestamp without time zone
);
    DROP TABLE public.admins;
       public         heap r       postgres    false                       0    0    TABLE admins    COMMENT     V   COMMENT ON TABLE public.admins IS 'System administrators with access to admin panel';
          public               postgres    false    218            �            1259    25107    admins_id_seq    SEQUENCE     �   CREATE SEQUENCE public.admins_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 $   DROP SEQUENCE public.admins_id_seq;
       public               postgres    false    218                       0    0    admins_id_seq    SEQUENCE OWNED BY     ?   ALTER SEQUENCE public.admins_id_seq OWNED BY public.admins.id;
          public               postgres    false    217            �            1259    25133 
   categories    TABLE     �   CREATE TABLE public.categories (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    description character varying(255),
    status character varying(20) DEFAULT 'Active'::character varying
);
    DROP TABLE public.categories;
       public         heap r       postgres    false                       0    0    TABLE categories    COMMENT     Y   COMMENT ON TABLE public.categories IS 'Categories for classifying lost and found items';
          public               postgres    false    222            �            1259    25132    categories_id_seq    SEQUENCE     �   CREATE SEQUENCE public.categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 (   DROP SEQUENCE public.categories_id_seq;
       public               postgres    false    222                       0    0    categories_id_seq    SEQUENCE OWNED BY     G   ALTER SEQUENCE public.categories_id_seq OWNED BY public.categories.id;
          public               postgres    false    221            �            1259    25174    claims    TABLE     �   CREATE TABLE public.claims (
    id integer NOT NULL,
    item_id integer NOT NULL,
    user_id integer,
    claim_date date NOT NULL,
    status character varying(50) NOT NULL
);
    DROP TABLE public.claims;
       public         heap r       postgres    false                       0    0    TABLE claims    COMMENT     I   COMMENT ON TABLE public.claims IS 'Claims made by users for lost items';
          public               postgres    false    228            �            1259    25173    claims_id_seq    SEQUENCE     �   CREATE SEQUENCE public.claims_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 $   DROP SEQUENCE public.claims_id_seq;
       public               postgres    false    228                       0    0    claims_id_seq    SEQUENCE OWNED BY     ?   ALTER SEQUENCE public.claims_id_seq OWNED BY public.claims.id;
          public               postgres    false    227            �            1259    25148    items    TABLE     �  CREATE TABLE public.items (
    id integer NOT NULL,
    category_id integer NOT NULL,
    description text NOT NULL,
    location_id integer NOT NULL,
    date_reported date NOT NULL,
    image_file character varying(255),
    rfid_tag character varying(255),
    status character varying(50) NOT NULL,
    owner_id integer,
    unique_code character varying(20),
    registration_date timestamp without time zone
);
    DROP TABLE public.items;
       public         heap r       postgres    false            	           0    0    TABLE items    COMMENT     L   COMMENT ON TABLE public.items IS 'Lost and found items with their details';
          public               postgres    false    226            �            1259    25147    items_id_seq    SEQUENCE     �   CREATE SEQUENCE public.items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 #   DROP SEQUENCE public.items_id_seq;
       public               postgres    false    226            
           0    0    items_id_seq    SEQUENCE OWNED BY     =   ALTER SEQUENCE public.items_id_seq OWNED BY public.items.id;
          public               postgres    false    225            �            1259    25141 	   locations    TABLE     d   CREATE TABLE public.locations (
    id integer NOT NULL,
    name character varying(50) NOT NULL
);
    DROP TABLE public.locations;
       public         heap r       postgres    false                       0    0    TABLE locations    COMMENT     R   COMMENT ON TABLE public.locations IS 'Physical locations where items were found';
          public               postgres    false    224            �            1259    25140    locations_id_seq    SEQUENCE     �   CREATE SEQUENCE public.locations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 '   DROP SEQUENCE public.locations_id_seq;
       public               postgres    false    224                       0    0    locations_id_seq    SEQUENCE OWNED BY     E   ALTER SEQUENCE public.locations_id_seq OWNED BY public.locations.id;
          public               postgres    false    223            �            1259    25119    users    TABLE     �  CREATE TABLE public.users (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    email character varying(100) NOT NULL,
    student_id character varying(50) NOT NULL,
    contact_number character varying(15),
    password character varying(255) NOT NULL,
    created_at timestamp without time zone,
    last_login timestamp without time zone,
    account_status character varying(20) DEFAULT 'Active'::character varying
);
    DROP TABLE public.users;
       public         heap r       postgres    false                       0    0    TABLE users    COMMENT     M   COMMENT ON TABLE public.users IS 'End users who can report and claim items';
          public               postgres    false    220            �            1259    25118    users_id_seq    SEQUENCE     �   CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 #   DROP SEQUENCE public.users_id_seq;
       public               postgres    false    220                       0    0    users_id_seq    SEQUENCE OWNED BY     =   ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;
          public               postgres    false    219            :           2604    25111 	   admins id    DEFAULT     f   ALTER TABLE ONLY public.admins ALTER COLUMN id SET DEFAULT nextval('public.admins_id_seq'::regclass);
 8   ALTER TABLE public.admins ALTER COLUMN id DROP DEFAULT;
       public               postgres    false    217    218    218            =           2604    25136    categories id    DEFAULT     n   ALTER TABLE ONLY public.categories ALTER COLUMN id SET DEFAULT nextval('public.categories_id_seq'::regclass);
 <   ALTER TABLE public.categories ALTER COLUMN id DROP DEFAULT;
       public               postgres    false    222    221    222            A           2604    25177 	   claims id    DEFAULT     f   ALTER TABLE ONLY public.claims ALTER COLUMN id SET DEFAULT nextval('public.claims_id_seq'::regclass);
 8   ALTER TABLE public.claims ALTER COLUMN id DROP DEFAULT;
       public               postgres    false    227    228    228            @           2604    25151    items id    DEFAULT     d   ALTER TABLE ONLY public.items ALTER COLUMN id SET DEFAULT nextval('public.items_id_seq'::regclass);
 7   ALTER TABLE public.items ALTER COLUMN id DROP DEFAULT;
       public               postgres    false    226    225    226            ?           2604    25144    locations id    DEFAULT     l   ALTER TABLE ONLY public.locations ALTER COLUMN id SET DEFAULT nextval('public.locations_id_seq'::regclass);
 ;   ALTER TABLE public.locations ALTER COLUMN id DROP DEFAULT;
       public               postgres    false    224    223    224            ;           2604    25122    users id    DEFAULT     d   ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);
 7   ALTER TABLE public.users ALTER COLUMN id DROP DEFAULT;
       public               postgres    false    219    220    220            �          0    25108    admins 
   TABLE DATA           n   COPY public.admins (id, username, password, email, full_name, "position", last_login, created_at) FROM stdin;
    public               postgres    false    218   K       �          0    25133 
   categories 
   TABLE DATA           C   COPY public.categories (id, name, description, status) FROM stdin;
    public               postgres    false    222   qK       �          0    25174    claims 
   TABLE DATA           J   COPY public.claims (id, item_id, user_id, claim_date, status) FROM stdin;
    public               postgres    false    228   �K       �          0    25148    items 
   TABLE DATA           �   COPY public.items (id, category_id, description, location_id, date_reported, image_file, rfid_tag, status, owner_id, unique_code, registration_date) FROM stdin;
    public               postgres    false    226   �K       �          0    25141 	   locations 
   TABLE DATA           -   COPY public.locations (id, name) FROM stdin;
    public               postgres    false    224   �K       �          0    25119    users 
   TABLE DATA           ~   COPY public.users (id, name, email, student_id, contact_number, password, created_at, last_login, account_status) FROM stdin;
    public               postgres    false    220   �K                  0    0    admins_id_seq    SEQUENCE SET     ;   SELECT pg_catalog.setval('public.admins_id_seq', 1, true);
          public               postgres    false    217                       0    0    categories_id_seq    SEQUENCE SET     @   SELECT pg_catalog.setval('public.categories_id_seq', 1, false);
          public               postgres    false    221                       0    0    claims_id_seq    SEQUENCE SET     <   SELECT pg_catalog.setval('public.claims_id_seq', 1, false);
          public               postgres    false    227                       0    0    items_id_seq    SEQUENCE SET     ;   SELECT pg_catalog.setval('public.items_id_seq', 1, false);
          public               postgres    false    225                       0    0    locations_id_seq    SEQUENCE SET     ?   SELECT pg_catalog.setval('public.locations_id_seq', 1, false);
          public               postgres    false    223                       0    0    users_id_seq    SEQUENCE SET     ;   SELECT pg_catalog.setval('public.users_id_seq', 1, false);
          public               postgres    false    219            C           2606    25115    admins admins_pkey 
   CONSTRAINT     P   ALTER TABLE ONLY public.admins
    ADD CONSTRAINT admins_pkey PRIMARY KEY (id);
 <   ALTER TABLE ONLY public.admins DROP CONSTRAINT admins_pkey;
       public                 postgres    false    218            E           2606    25117    admins admins_username_key 
   CONSTRAINT     Y   ALTER TABLE ONLY public.admins
    ADD CONSTRAINT admins_username_key UNIQUE (username);
 D   ALTER TABLE ONLY public.admins DROP CONSTRAINT admins_username_key;
       public                 postgres    false    218            M           2606    25139    categories categories_pkey 
   CONSTRAINT     X   ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (id);
 D   ALTER TABLE ONLY public.categories DROP CONSTRAINT categories_pkey;
       public                 postgres    false    222            X           2606    25179    claims claims_pkey 
   CONSTRAINT     P   ALTER TABLE ONLY public.claims
    ADD CONSTRAINT claims_pkey PRIMARY KEY (id);
 <   ALTER TABLE ONLY public.claims DROP CONSTRAINT claims_pkey;
       public                 postgres    false    228            T           2606    25155    items items_pkey 
   CONSTRAINT     N   ALTER TABLE ONLY public.items
    ADD CONSTRAINT items_pkey PRIMARY KEY (id);
 :   ALTER TABLE ONLY public.items DROP CONSTRAINT items_pkey;
       public                 postgres    false    226            V           2606    25157    items items_unique_code_key 
   CONSTRAINT     ]   ALTER TABLE ONLY public.items
    ADD CONSTRAINT items_unique_code_key UNIQUE (unique_code);
 E   ALTER TABLE ONLY public.items DROP CONSTRAINT items_unique_code_key;
       public                 postgres    false    226            O           2606    25146    locations locations_pkey 
   CONSTRAINT     V   ALTER TABLE ONLY public.locations
    ADD CONSTRAINT locations_pkey PRIMARY KEY (id);
 B   ALTER TABLE ONLY public.locations DROP CONSTRAINT locations_pkey;
       public                 postgres    false    224            G           2606    25129    users users_email_key 
   CONSTRAINT     Q   ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);
 ?   ALTER TABLE ONLY public.users DROP CONSTRAINT users_email_key;
       public                 postgres    false    220            I           2606    25127    users users_pkey 
   CONSTRAINT     N   ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);
 :   ALTER TABLE ONLY public.users DROP CONSTRAINT users_pkey;
       public                 postgres    false    220            K           2606    25131    users users_student_id_key 
   CONSTRAINT     [   ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_student_id_key UNIQUE (student_id);
 D   ALTER TABLE ONLY public.users DROP CONSTRAINT users_student_id_key;
       public                 postgres    false    220            Y           1259    25193    idx_claims_item_id    INDEX     H   CREATE INDEX idx_claims_item_id ON public.claims USING btree (item_id);
 &   DROP INDEX public.idx_claims_item_id;
       public                 postgres    false    228            Z           1259    25194    idx_claims_user_id    INDEX     H   CREATE INDEX idx_claims_user_id ON public.claims USING btree (user_id);
 &   DROP INDEX public.idx_claims_user_id;
       public                 postgres    false    228            P           1259    25190    idx_items_category_id    INDEX     N   CREATE INDEX idx_items_category_id ON public.items USING btree (category_id);
 )   DROP INDEX public.idx_items_category_id;
       public                 postgres    false    226            Q           1259    25191    idx_items_location_id    INDEX     N   CREATE INDEX idx_items_location_id ON public.items USING btree (location_id);
 )   DROP INDEX public.idx_items_location_id;
       public                 postgres    false    226            R           1259    25192    idx_items_owner_id    INDEX     H   CREATE INDEX idx_items_owner_id ON public.items USING btree (owner_id);
 &   DROP INDEX public.idx_items_owner_id;
       public                 postgres    false    226            ^           2606    25180    claims claims_item_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.claims
    ADD CONSTRAINT claims_item_id_fkey FOREIGN KEY (item_id) REFERENCES public.items(id) ON DELETE CASCADE;
 D   ALTER TABLE ONLY public.claims DROP CONSTRAINT claims_item_id_fkey;
       public               postgres    false    228    4692    226            _           2606    25185    claims claims_user_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.claims
    ADD CONSTRAINT claims_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;
 D   ALTER TABLE ONLY public.claims DROP CONSTRAINT claims_user_id_fkey;
       public               postgres    false    220    4681    228            [           2606    25158    items items_category_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.items
    ADD CONSTRAINT items_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(id) ON DELETE CASCADE;
 F   ALTER TABLE ONLY public.items DROP CONSTRAINT items_category_id_fkey;
       public               postgres    false    222    4685    226            \           2606    25163    items items_location_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.items
    ADD CONSTRAINT items_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.locations(id) ON DELETE CASCADE;
 F   ALTER TABLE ONLY public.items DROP CONSTRAINT items_location_id_fkey;
       public               postgres    false    224    4687    226            ]           2606    25168    items items_owner_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.items
    ADD CONSTRAINT items_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.users(id) ON DELETE SET NULL;
 C   ALTER TABLE ONLY public.items DROP CONSTRAINT items_owner_id_fkey;
       public               postgres    false    4681    226    220            �   Y   x�3�t-JL��LL����LO-J�Iq s���s9��
~�U
�y)��y��`�1~�FF������
�VFfV�z�Ɩ�F�\1z\\\ &BY      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �     