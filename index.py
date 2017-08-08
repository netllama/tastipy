import datetime
import re
from cgi import escape
import HTMLParser
import psycopg2
import psycopg2.extras
from bottle import route, request, get, post, response
from math import ceil
import hashlib


CONN_STRING = 'host=127.0.0.1 dbname=tasti user=tasti password="" port=5432'

def get_index():
    """Returns main page/index content."""
    base_url = 'http://{se}{sc}/'.format(se=request.environ.get('SERVER_NAME'), sc=request.environ.get('SCRIPT_NAME'))
    return_data = ''
    top = '''<html lang="en">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>Tasti</title>
    <link rel="stylesheet" type="text/css" href="{h}css/main.css" />
</head>
<body><div id="wrapper">
        <div id="header">'''.format(h=base_url)
    return_data += top
    return_data += header0()
    return_data += '''</div>
    <div id="faux">
        <div id="leftcolumn">'''
    return_data += do_bmarks()
    return_data += '''<div class="clear"></div>
        </div>
        <div id="rightcolumn">
                '''
    return_data += list_tags()
    return_data += '''<div class="clear"></div>
        </div>
    </div>
    <div id="footer">'''
    return_data += footer()

    bottom = '''</div>
    </div>
</body>
</html>
    '''
    return_data += bottom
    return return_data


def header0():
    """Header content."""
    base_url = 'http://{se}{sc}/'.format(se=request.environ.get('SERVER_NAME'),
                                         sc=request.environ.get('SCRIPT_NAME'))
    auth_payload = auth_check()
    if auth_payload['is_authenticated']:
        header_string = '''&nbsp;Hi <A HREF="{h}account">{u}</a>&nbsp;|&nbsp;<A HREF="{h}login?do=1">Logout</a><BR><BR>
                           <UL><LI><A HREF="{h}add">ADD</a>&nbsp;a&nbsp;bookmark<LI>
                           <A HREF="{h}bmarks?whose=mine">MY BOOKMARKS</a></UL>'''.format(h=base_url,
                                                                                          u=auth_payload['username'])
    else:
        header_string = '''&nbsp;<A HREF="{h}login?do=0">Login</a>
                           &nbsp;|&nbsp;<A HREF="{h}register">Register</a>&nbsp;'''.format(h=base_url)
    return_data = '''<span class="header_class1"><TABLE width="100%"><TR>
    <TD><A HREF="{h}"><IMG SRC="{h}images/tasti-logo.png"></a></TD>
    <TD>&nbsp;</TD><TD align="right" valign="top">{header}</TD>
    </TR></TABLE></span>'''.format(header=header_string,
                                   h=base_url)
    return return_data


def do_tags():
    """Show bookmarks associated with a tag."""
    base_url = 'http://{se}{sc}/'.format(se=request.environ.get('SERVER_NAME'),
                                         sc=request.environ.get('SCRIPT_NAME'))
    user_num_bmarks = 15
    num_bmarks_menu_offset = 53
    return_data = ''
    tag_id = ''
    tag_get = ''
    show_mine = ''
    auth = auth_check()
    if request.query.get('id'):
        tag_id = request.query.get('id')
        tag_get = '&id={}'.format(tag_id)
    tags_sql = 'SELECT tag FROM tags '
    if hash_check():
        username = request.get_cookie('tasti_username').lower()
        if request.query.get('mine') and request.query.get('mine') == 'yes':
            show_mine = "AND owner='{}'".format(username)
            num_bmarks_menu_offset = 60
        if tag_id:
            tags_sql += "WHERE id='{t}' {m} LIMIT 1".format(t=tag_id,
                                                            m=show_mine)
        else:
            tags_sql += 'WHERE true=true {m} ORDER BY id DESC LIMIT 1'.format(m=show_mine)
    else:
        username = ''
        if tag_id:
            tags_sql += "WHERE id='{t}' LIMIT 1".format(t=tag_id)
        else:
            tags_sql += 'ORDER BY id DESC LIMIT 1'
    tags_qry = db_qry([tags_sql, None], 'select')
    if not tags_qry:
        return_data += '<span class="bad">Tags query FAILED:<BR>{}<BR>'.format(tags_sql)
        return return_data
    tag_count = len(tags_qry)
    if tag_count:
        tags = [t[0] for t in tags_qry]
        if request.get_cookie('tasti_bmarks_per_page'):
            bmarks_per_page = request.get_cookie('tasti_bmarks_per_page')
        if request.query.get('num') and re.match('\d', request.query.get('num')):
            user_num_bmarks = request.query.get('num')
            # 190 days until expiration
            cookie_expire = datetime.datetime.now() + datetime.timedelta(days=190)
            response.set_cookie('tasti_bmarks_per_page', user_num_bmarks, expires=cookie_expire)   
        limit_sql = ' LIMIT {}'.format(user_num_bmarks)
        marker_dict = get_markers(user_num_bmarks)  
        # pagination setup
        page = 1
        if request.query.get('page'):
            page = int(request.query.get('page'))
        prev = int(page) - 1
        next = int(page) + 1
        max_results = user_num_bmarks
        # Calculate the offset
        from_offset = (int(page) * int(max_results)) - int(max_results)
        url_get_base = '{h}tags?{u}'.format(h=base_url,
                                            u=request.environ.get('QUERY_STRING'))
        tag = tags[0]
        bmarks_sql_base = "SELECT id, date(last_update) as last_update, owner, url, notes, name FROM bmarks WHERE tag='{t}' ".format(t=tag)
        if username and request.query.get('mine') and request.query.get('mine') == 'yes':
            bmarks_sql_base += " AND owner='{u}' ".format(u=username)
            mine = '&mine=yes'
        else:
            mine = ''
        bmarks_sql_all = '{bm} ORDER BY owner, last_update, name'.format(bm=bmarks_sql_base)
        bmarks_sql = '{bm} {l} OFFSET {o}'.format(bm=bmarks_sql_all, l=limit_sql, o=from_offset)
        bmarks_qry = db_qry([bmarks_sql, None], 'select')
        if not bmarks_qry:
            return_data += '<span class="bad">Bmarks query FAILED:<BR>{}<BR>'.format(bmarks_sql)
            return return_data
        bmarks_qry_all_res = db_qry([bmarks_sql_all, None], 'select')
        if not bmarks_qry_all_res:
            return_data += '<span class="bad">Bmarks All query FAILED:<BR>{}<BR>'.format(bmarks_sql_all)
            return return_data
        num_bmarks_all = len(bmarks_qry_all_res)
        num_bmarks = len(bmarks_qry)
        if num_bmarks:
            left_td_width = 100 - (22 + len(tag))
            return_data += '''<TABLE width="100%"><TR>
                                <TD width="{lw}%">
                                <span class="huge">Bookmarks tagged with <B>{t}</B></span></TD>'''.format(lw=left_td_width, t=tag)
            # only render the bmarks/page menu on the 'MY BOOKMARKS' page
            if hash_check():
                return_data += '''<TD valign="top"><div id="menu">
                                    <UL id="item1">
                                    <LI class="top"><B>Bookmarks/page</B></LI>
                                        <LI class="item"><A HREF="{u}&num=5">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{a5}5&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</a></LI>
                                        <LI class="item"><A HREF="{u}&num=10">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{a10}10&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</a></LI>
                                        <LI class="item"><A HREF="{u}&num=15">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{a15}15&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</a></LI>
                                        <LI class="item"><A HREF="{u}&num=20">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{a20}20&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</a></LI>
                                        <LI class="item"><A HREF="{u}&num=30">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{a30}30&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</a></LI></UL>
                                    </DIV>&nbsp;</TD>'''.format(n=num_bmarks_menu_offset,
                                                                u=url_get_base,
                                                                a5=marker_dict['5'],
                                                                a10=marker_dict['10'],
                                                                a15=marker_dict['15'],
                                                                a20=marker_dict['20'],
                                                                a30=marker_dict['30'])
            return_data += '</TR></TABLE><HR><BR>'
            for bmark_row in bmarks_qry:
                notes_string = ''
                bm_id = bmark_row[0]
                last_update = bmark_row[1]
                owner = bmark_row[2]
                url = bmark_row[3]
                notes = bmark_row[4].replace('&amp;quot;', '"').replace('&amp;#039;', "'")
                name = bmark_row[5].replace('&amp;quot;', '"').replace('&amp;#039;', "'")
                if notes:
                    notes_string = '<BR><span class="small"><B>{n}</B></span>'.format(n=notes)
                if hash_check() and owner == username:
                    bmark_user_edit_string = '''<BR><A HREF="edit?id={i}&func=edit"><span class="normal"><B>EDIT</B></a>
                                                &nbsp;|&nbsp;<A HREF="{h}bmarks?id={i}&func=del"><B>DELETE</B></a>&nbsp;</span>'''.format(i=bm_id,
                                                                                                                                          h=base_url)
                else:
                    bmark_user_edit_string = '''<BR><span class="normal">Created by <A HREF="{h}bmarks?whose={o}">
                                                <B>{o}</B></a>&nbsp;</span>'''.format(o=owner,
                                                                                      h=base_url)
                return_data += '''<TABLE><TR>
                                    <TD valign="top" width="95"><span class="big">{l}&nbsp;&nbsp;&nbsp;</span></TD>
                                    <TD><span class="big"><A HREF="{u}">{n}</a></span>{no}{b}</TD>
                                </TR></TABLE><HR><BR>'''.format(l=last_update, u=url,
                                                                n=name, no=notes_string,
                                                                b=bmark_user_edit_string)
            # pagination settings
            my_row_count = num_bmarks_all
            total_pages = int(ceil(int(my_row_count) / float(max_results)))
            pagination = ''

            # Create a PREV link if one is needed
            if page > 1:
                pagination += '''<A STYLE="text-decoration:none" title="PREVIOUS PAGE" HREF="{h}tags?{m}&page={p}&num={u}{t}">
                                 <span class="huge"><H1>&larr;</H1></span></A>'''.format(m=mine,
                                                                                         p=prev,
                                                                                         u=user_num_bmarks,
                                                                                         h=base_url,
                                                                                         t=tag_get)
            # Create a NEXT link if one is needed
            if page < total_pages:
                pagination += '''<A STYLE="text-decoration:none" title="NEXT PAGE" HREF="{h}tags?{m}&page={n}&num={u}{t}">
                                 <span class="huge"><H1>&rarr;</H1></span></A>'''.format(m=mine, n=next, u=user_num_bmarks,
                                                                                         h=base_url, t=tag_get)
            else:
                # adjust the total count when on the last page since
                # it might not have user_num_bmarks items remaining
                new_max_results = (int(max_results) - ((int(page) * int(max_results)) - int(my_row_count)))
                max_results = new_max_results
            plural = ''
            if my_row_count:
                plural = 's'
            return_data += '''<TABLE width="100%"><TR COLSPAN="1"><TD>&nbsp;</TD></TR>
                            <TR><TD COLSPAN="9">&nbsp;{m} Tasti bookmark{p}</TD>
                            <TD class="page" COLSPAN="4"><B>{pa}</B></TD></TR></TABLE><BR>'''.format(m=my_row_count,
                                                                                                     p=plural,
                                                                                                     pa=pagination)
    else:
        return_data += 'No tags selected.<BR><BR><BR>'
    return return_data


def do_bmarks():
    """Bookmark content."""
    return_data = ''
    auth = auth_check()
    
    if auth['is_authenticated'] and auth['username'] and request.query.get('func') and request.query.get('id'):
    	username = auth['username']
        bmark_id = request.query.get('id')
        if request.query.get('func') == 'del':
            old_bmark_sql = "SELECT created, url, notes, name FROM bmarks WHERE id='{i}' LIMIT 1".format(i=bmark_id)
            old_bmark_res = db_qry([old_bmark_sql, None], 'select')
            if not old_bmark_res:
            	return_data += '''<span class="bad">Old Bookmark query FAILED<BR>{}<BR></span>
                                  <BR><BR>'''.format(old_bmark_sql)
                return return_data
            old_bmark = old_bmark_res[0]
            old_created = old_bmark[0]
            old_url = old_bmark[1]
            old_notes = old_bmark[2]
            old_name = old_bmark[3]
            bmark_del_sql = 'DELETE FROM bmarks WHERE id=%s AND owner=%s'
            del_sql_vals = [bmark_id, username]
            bmark_del_qry = db_qry([bmark_del_sql, del_sql_vals], 'del')
            if not bmark_del_qry:
            	# delete failed
            	return_data += '''<span class="bad">Bookmark ( {n} ) deletion FAILED<BR>{s}</span>
                                  <BR><BR>'''.format(n=old_name, s=bmark_del_sql)
            else:
            	return_data += '''<span class="huge">Bookmark ( {o} ) successfully deleted</span>
                                  <BR><BR>'''.format(o=old_name)
    else:
    	return_data += show_bmarks()
    return return_data


def list_tags():
    """List tags.

	only the user's, if logged in,
    most recently added otherwise
    """
    return_data = ''
    base_url = 'http://{se}{sc}/'.format(se=request.environ.get('SERVER_NAME'), sc=request.environ.get('SCRIPT_NAME'))
    auth = auth_check()
    tags_sql_base = 'SELECT id, tag FROM tags '
    if auth['is_authenticated'] and auth['username']:
		tags_sql = "{s} WHERE owner='{u}' ORDER BY tag".format(s=tags_sql_base, u=auth['username'])
    else:
		tags_sql = "{s} ORDER BY last_update, tag LIMIT 50".format(s=tags_sql_base)
    tags_qry_res = db_qry([tags_sql, None], 'select')
    if not tags_qry_res:
    	return_data += '<span class="bad">Tags query FAILED<BR>'
        return return_data
    else:
    	if auth['username']:
            tag_string = '<span class="big"><B>Your Tags</B></span><BR><BR>'
            show_mine = '&mine=yes'
        else:
            tag_string = '<span class="big"><B>Recent Tags</B></span><BR><BR>'
            show_mine = ''
        num_tags = len(tags_qry_res)
        if num_tags:
            return_data += tag_string
            for tag_list in tags_qry_res:
            	tag_id = tag_list[0]
                tag = tag_list[1]
            	return_data += '&nbsp;&nbsp;<A HREF="{h}tags?id={i}{sh}">{t}</a>&nbsp;<BR>'.format(i=tag_id,
                                                                                                sh=show_mine,
                                                                                                t=tag,
                                                                                                h=base_url)
        return_data += '<BR>'
    return return_data


def get_markers(user_num_bmarks):
    """Get marker values."""
    marker_dict = {}
    vals = range(5, 35, 5)
    for val in vals:
        bmark_val = ''
        if val == int(user_num_bmarks):
            bmark_val = '*'
        marker_dict['{}'.format(val)] = bmark_val
    return marker_dict


def show_bmarks():
    """Show bookmarks."""
    base_url = 'http://{se}{sc}/'.format(se=request.environ.get('SERVER_NAME'), sc=request.environ.get('SCRIPT_NAME'))
    user_num_bmarks = 15
    mine = 'mine'
    whose = ''
    default_num_bmarks_menu_offset = 77
    return_data = ''
    if request.get_cookie('tasti_bmarks_per_page'):
        bmarks_per_page = request.get_cookie('tasti_bmarks_per_page')
    if request.query.get('num') and re.match('\d', request.query.get('num')):
        user_num_bmarks = request.query.get('num')
        # 190 days until expiration
        cookie_expire = datetime.datetime.now() + datetime.timedelta(days=190)
        response.set_cookie('tasti_bmarks_per_page', user_num_bmarks, expires=cookie_expire)
    limit_sql = ' LIMIT {}'.format(user_num_bmarks)
    marker_dict = get_markers(user_num_bmarks)
    # pagination setup
    page = 1
    if request.query.get('page'):
        page = int(request.query.get('page'))
    prev = int(page) - 1
    next = int(page) + 1
    max_results = user_num_bmarks
    # Calculate the offset
    from_offset = (int(page) * int(max_results)) - int(max_results)
    url_get_base = '{h}bmarks?{u}'.format(h=base_url,
                                   u=request.environ.get('QUERY_STRING'))
    bmarks_sql_base = '''SELECT distinct ON (url) url, id, date(last_update) AS last_update, notes, name, owner
                        FROM bmarks'''
    if hash_check():
        username = request.get_cookie('tasti_username').lower()
    if request.query.get('whose') and request.query.get('whose') == mine and hash_check():
        whose = request.query.get('whose')
        url_get_base += '&'
        num_bmarks_menu_offset = default_num_bmarks_menu_offset
        bmarks_intro = '<span class="huge">Your bookmarks:</span><BR><BR>'
        bmarks_sql_all = '''{s} WHERE owner='{u}' ORDER BY url, last_update'''.format(s=bmarks_sql_base,
                                                                                      u=username)
    elif request.query.get('whose') and request.query.get('whose') != mine:
        whose = request.query.get('whose')
        url_get_base += '&'
        num_bmarks_menu_offset = 177
        bmarks_intro = '''<span class="huge">{o}'s&nbsp;bookmarks:</span><BR><BR>'''.format(o=whose)
        bmarks_sql_all = '''{s} WHERE owner='{u}' ORDER BY url, last_update'''.format(s=bmarks_sql_base,
                                                                                      u=whose)
    else:
        num_bmarks_menu_offset = 73
        url_get_base += '?'
        bmarks_intro = '<span class="huge">Recent bookmarks:</span><BR><BR>'
        bmarks_sql_all = '{s} ORDER BY url, last_update'.format(s=bmarks_sql_base)
    bmarks_sql = '{s} {l} OFFSET {o}'.format(s=bmarks_sql_all,
                                             l=limit_sql,
                                             o=from_offset)
    bmarks_qry = db_qry([bmarks_sql, None], 'select')
    if not bmarks_qry:
        return_data += '<span class="bad">Bmarks query FAILED:<BR>{}<BR>'.format(bmarks_sql)
        return return_data
    bmarks_qry_all_res = db_qry([bmarks_sql_all, None], 'select')
    if not bmarks_qry_all_res:
        return_data += '<span class="bad">Bmarks All query FAILED<BR>{}<BR>'.format(bmarks_sql_all)
        return return_data
    num_bmarks_all = len(bmarks_qry_all_res)
    num_bmarks = len(bmarks_qry)
    if num_bmarks:
        return_data += '<TABLE><TR><TD>{b}</TD>'.format(b=bmarks_intro)
        # only render the bmarks/page menu on the 'MY BOOKMARKS' page
        if num_bmarks_menu_offset == default_num_bmarks_menu_offset:
            return_data += '''<TD width="{n}%">&nbsp;</TD><TD align="center" valign="top"><div id="menu">
                                <UL id="item1">
                                <LI class="top"><B>Bookmarks/page</B></LI>
                                        <LI class="item"><A HREF="{u}num=5">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{a5}5&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</a></LI>
                                        <LI class="item"><A HREF="{u}num=10">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{a10}10&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</a></LI>
                                        <LI class="item"><A HREF="{u}num=15">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{a15}15&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</a></LI>
                                        <LI class="item"><A HREF="{u}num=20">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{a20}20&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</a></LI>
                                        <LI class="item"><A HREF="{u}num=30">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{a30}30&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</a></LI></UL>
                                </DIV>&nbsp;</TD>'''.format(n=num_bmarks_menu_offset,
                                                            u=url_get_base,
                                                            a5=marker_dict['5'],
                                                            a10=marker_dict['10'],
                                                            a15=marker_dict['15'],
                                                            a20=marker_dict['20'],
                                                            a30=marker_dict['30'])
        return_data += '</TR></TABLE>'
        for bmark_row in bmarks_qry:
            notes_string = ''
            url = bmark_row[0]
            bm_id = bmark_row[1]
            last_update = bmark_row[2]
            notes = bmark_row[3].replace('&amp;quot;', '"').replace('&amp;#039;', "'")
            name = bmark_row[4].replace('&amp;quot;', '"').replace('&amp;#039;', "'")
            owner = bmark_row[5]
            tags_sql = "SELECT tag FROM bmarks WHERE url='{u}' ".format(u=url)
            if hash_check() and request.query.get('whose') and request.query.get('whose') == mine:
                tags_sql += "AND owner='{u}' ".format(u=username)
                bmark_user_edit_string = '''<BR><A HREF="edit?id={i}&func=edit"><span class="normal"><B>EDIT</B></a>
                                            &nbsp;|&nbsp;<A HREF="{h}bmarks?id={i}&func=del"><B>DELETE</B></a>&nbsp;</span>'''.format(i=bm_id,
                                                                                                                                      h=base_url)
            else:
                bmark_user_edit_string = '''<BR><span class="normal">Created by <A HREF="{h}bmarks?whose={o}">
                                            <B>{o}</B></a>&nbsp;</span>'''.format(o=owner,
                                                                                  h=base_url)
            tags_sql += 'AND length(tag)>0 GROUP BY tag ORDER BY tag LIMIT 15'
            tags_qry = db_qry([tags_sql, None], 'select')
            if notes:
                notes_string = '<BR><span class="small"><B>{n}</B></span>'.format(n=notes)
            return_data += '''<TABLE><TR><TD valign="top"><span class="big">{l}&nbsp;&nbsp;&nbsp;</span></TD>
                                <TD width="65%"><span class="big"><A HREF="{u}">{n}</a></span>
                                {no}{b}</TD>'''.format(l=last_update, u=url, n=name,
                                                       no=notes_string, b=bmark_user_edit_string)
            num_tags = len(tags_qry)
            if num_tags:
                return_data += '<TD width="95%" valign="top" align="right">'
                tag_counter = 0
                for tag_row in tags_qry:
                    tag = tag_row[0]
                    tag_sql = "SELECT id FROM tags WHERE tag='{t}' ".format(t=tag)
                    if hash_check() and request.query.get('whose'):
                        sql_owner = request.query.get('whose')
                        if request.query.get('whose') == 'mine':
                            sql_owner = username
                        tag_sql += "AND owner='{u}'".format(u=sql_owner)
                    tag_sql += 'ORDER BY id LIMIT 1'
                    tag_qry_res = db_qry([tag_sql, None], 'select')
                    if not tag_qry_res:
                        return_data += '<span class="bad">Tags query FAILED:<BR>{}<BR>'.format(tag_sql)
                        return return_data
                    tag_id = tag_qry_res[0][0]
                    return_data += '<A HREF="{h}tags?id={tid}">{t}</a>&nbsp;&nbsp;'.format(tid=tag_id,
                                                                                           t=tag,
                                                                                           h=base_url)
                    tag_counter += 1
                    if tag_counter > 4:
                        tag_counter = 0
                        return_data += '<BR>'
                return_data += '&nbsp;</TD>'
            return_data += '</TR></TABLE><HR><BR>'
        # pagination settings
        my_row_count = num_bmarks_all
        total_pages = ceil(int(my_row_count) / int(max_results))
        pagination = ''

        # Create a PREV link if one is needed
        if page > 1:
            pagination += '''<A STYLE="text-decoration:none" title="PREVIOUS PAGE" HREF="{h}bmarks?whose={w}&page={p}&num={u}">
                             <span class="huge"><H1>&larr;</H1></span></A>'''.format(w=whose,
                                                                                     p=prev,
                                                                                     u=user_num_bmarks,
                                                                                     h=base_url)
        if not request.query.get('whose'):
            page = 0
            total_pages = 0
        # Create a NEXT link if one is needed
        if page < total_pages:
            pagination += '''<A STYLE="text-decoration:none" title="NEXT PAGE" HREF="{h}bmarks?whose={w}&page={n}&num={u}">
                             <span class="huge"><H1>&rarr;</H1></span></A>'''.format(w=whose, n=next, u=user_num_bmarks,
                                                                                     h=base_url)
        else:
            # adjust the total count when on the last page since
            # it might not have user_num_bmarks items remaining
            new_max_results = (int(max_results) - ((int(page) * int(max_results)) - int(my_row_count)))
            max_results = new_max_results
        plural = ''
        if my_row_count:
            plural = 's'
        return_data += '''<TABLE width="100%"><TR COLSPAN="1"><TD>&nbsp;</TD></TR>
                          <TR><TD COLSPAN="9">&nbsp;{m} Tasti bookmark{p}</TD>
                          <TD class="page" COLSPAN="4"><B>{pa}</B></TD></TR></TABLE><BR>'''.format(m=my_row_count,
                                                                                                   p=plural,
                                                                                                   pa=pagination)
    else:
        return_data += '<BR>There are currently no bookmarks<BR><BR>'
    return return_data


def do_add():
    """Add new bookmark content."""
    return_data = ''
    base_url = 'http://{se}{sc}/'.format(se=request.environ.get('SERVER_NAME'),
                                         sc=request.environ.get('SCRIPT_NAME'))
    auth_payload = auth_check()
    if auth_payload['is_authenticated'] and hash_check():
        username = request.get_cookie('tasti_username').lower()
        if request.method == 'POST' and request.forms.get('url'):
            return_data += add_bmark_db(username)
        return_data += add_bmark_form(base_url, request.get_cookie('tasti_username').lower())
    else:
        return_data += '''Only users who have <A HREF="{h}login?do=0">logged in</a>
                          may add new bookmarks.<BR>'''.format(h=base_url)
    return return_data


def add_bmark_form(base_url, username):
    """Generate form for adding a new bookmark."""
    name = ''
    url = ''
    return_data = ''
    if request.method == 'GET':
        if request.query.get('url'):
            url = request.query.get('url').strip()
        if request.query.get('name'):
            name = escape(request.query.get('name').strip(), quote=True)
    # get list of pre-existing tags for the user
    tags_sql = "SELECT tag FROM tags WHERE owner='{u}' ORDER BY tag LIMIT 150".format(u=username)
    tags_qry = db_qry([tags_sql, None], 'select')
    # generate add bookmark form
    return_data += '''<span class="huge">Add a new bookmark to <B>Tasti</B>:</span><BR><BR> 
                        <FORM method="POST" action="{u}add" id="add_bmark"><TABLE>'''.format(u=base_url)
    return_data += '''<TR><TD>Name/Description*:&nbsp;</TD>
                          <TD>&nbsp;</TD>
                          <TD><INPUT TYPE="text" name="name" id="name" size="55" value="{n}"></TD>
                      </TR>'''.format(n=name)
    return_data += '''<TR><TD>URL*:&nbsp;</TD>
                          <TD>&nbsp;</TD>
                          <TD><INPUT TYPE="text" name="url" id="url" size="55" value="{u}"></TD>
                      </TR>'''.format(u=url)
    return_data += '''<TR><TD>Notes:&nbsp;</TD>
                          <TD>&nbsp;</TD>
                          <TD><INPUT TYPE="text" name="notes" id="notes" size="55"></TD></TR>
		              <TR><TD>Tags:&nbsp;</TD>
                          <TD>&nbsp;</TD>
                          <TD><INPUT TYPE="text" name="tags" id="tags" size="55"></TD></TR>
		              <TR><TD>&nbsp;</TD>
                          <TD>&nbsp;</TD>
                          <TD>&nbsp;</TD>
                          <TD>&nbsp;</TD></TR>
		              <TR><TD>&nbsp;</TD>
                          <TD><DIV class="submit"><INPUT type="submit" value="Add" /></TD>
                          <TD>&nbsp;</TD></TR>
	                  </TABLE></FORM><BR>
                      <span class="tiny">&nbsp;* Required field</span><BR><BR>'''
    # display a clickable list of the user's tags that
    # can be clicked to be added to the Tags form field above
    if tags_qry:
        html_parser = HTMLParser.HTMLParser()
        tag_counter = 0
        max_tags_per_row = 10
        return_data += '''<span class="big">Click below to add one (or more) of your 
                        pre-existing tags to the new bookmark above:</span><BR><BR>'''
        for raw_tag_name in tags_qry:
            tag_name = html_parser.unescape(raw_tag_name[0]).strip()
            return_data += '''<A onclick="document.getElementById('tags').value=document.getElementById('tags').value + ' ' + '{t}';">
                              {t}</a>&nbsp;&nbsp;'''.format(t=tag_name)
            tag_counter += 1
            if tag_counter >= max_tags_per_row:
                # start new row of tags
                return_data += '<BR>'
                tag_counter = 1
        return_data += '<BR><BR><BR>'
    return return_data


def add_bmark_db(username):
    """Insert new bookmark into database."""
    return_data = ''
    bmark_name = escape(request.forms.get('name'), quote=True)
    bmark_url = request.forms.get('url')
    bmark_note = ''
    if request.forms.get('notes'):
        bmark_note = escape(request.forms.get('notes').strip(), quote=True)
    bmark_tags_list = []
    if request.forms.get('tags'):
        # convert space separated tags into unique list
        bmark_tags_list = set(request.forms.get('tags').strip().split(' '))
    for raw_tag in bmark_tags_list:
        # insert new tags and bookmark into database
        tag = escape(raw_tag.strip(), quote=True)
        user_has_tag_sql = "SELECT id FROM tags WHERE owner='{u}' AND tag='{t}'".format(u=username,
                                                                                        t=tag)
        user_has_tag_qry = db_qry([user_has_tag_sql, None], 'select')
        if len(user_has_tag_qry) == 0 and tag:
            # tag doesn't exist, so insert it
            add_user_tag_sql = 'INSERT INTO tags (owner, tag) VALUES (%s, %s)'
            add_user_tag_vals = [username, tag]
            add_user_tag_qry = db_qry([add_user_tag_sql, add_user_tag_vals], 'insert')
            if add_user_tag_qry is False:
                return_data += '<span class="bad">Failed to insert new tag ({t})<BR>{s}<BR></span>'.format(t=tag,
                                                                                                           s=add_user_tag_sql)
                continue
        add_bmark_sql = 'INSERT INTO bmarks (owner, url, notes, tag, name) VALUES (%s, %s, %s, %s, %s)'
        add_bmark_vals = [username, bmark_url, bmark_note, tag, bmark_name]
        add_bmark_qry = db_qry([add_bmark_sql, add_bmark_vals], 'insert')
        if add_bmark_qry:
            return_data += 'Bookmark <B>( {b} )</B> successfully added!'.format(b=bmark_name)
        else:
            # insert failed
            return_data += '<span class="bad">Failed to insert new bookmark ({b})<BR>{s}<BR></span>'.format(b=bmark_name,
                                                                                                            s=add_bmark_sql)
    return return_data


def generate_tabs():
    """Generate tab content structure."""
    return_data = ''
    account_selected = ''
    import_selected = ''
    bmarklet_selected = ''
    tag_selected = ''
    ie_comment = 'these comments between lis solve a bug in IE that prevents spaces appearing between list items that appear on different lines in the source'
    base_url = 'http://{se}{sc}/'.format(se=request.environ.get('SERVER_NAME'),
                                         sc=request.environ.get('SCRIPT_NAME'))
    selected = 'id="selected"'
    script = request.environ.get('SCRIPT_URL').split('/')[-1]
    if script == 'account':
        account_selected = selected
    if script == 'import':
        import_selected = selected
    if script == 'bmarklet':
        bmarklet_selected = selected
    if script == 'edit_tags':
        tag_selected = selected
    return_data += '''<div id="tabs"><ul>
		              <li {a}><a href="{bu}account">Details</a></li><!-- {c} -->
                      <li {i}><a href="{bu}import">Import&nbsp;Bookmarks</a></li><!-- {c} -->
                      <li {b}><a href="{bu}bmarklet">Bookmarklet</a></li><!-- {c} -->
                      <li {t}><a href="{bu}edit_tags">Tags</a></li><!-- -->
                      </ul></div>'''.format(bu=base_url,
                                            a=account_selected,
                                            i=import_selected,
                                            b=bmarklet_selected,
                                            t=tag_selected,
                                            c=ie_comment)
    return return_data


def account_details_form(username, base_url):
    """Render account details form content."""
    name = ''
    email = ''
    return_data = ''
    account_sql = "SELECT name, email FROM users WHERE username='{u}' ORDER BY username LIMIT 1".format(u=username)
    account_qry = db_qry([account_sql, None], 'select')
    if not account_qry:
        return_data += 'Account select failed:<BR>{s}<BR>'.format(s=account_sql)
        return return_data
    name = account_qry[0][0]
    email = account_qry[0][1]
    return_data += '''<div id="content"><span class="big">Please edit the fields that you wish to change for your <B>
                        Tasti</B> account:</span><BR><BR>
                        <FORM method="POST" action="{bu}account" id="register"><TABLE>
			            <TR><TD><label for="password0">Change your Password (at least 6 characters):&nbsp;</label></TD>
                            <TD>&nbsp;</TD><TD><INPUT NAME="password0" TYPE="password" id="password0" /></TD></TR>
			            <TR><TD><label for="password1">Enter the new password again:&nbsp;</label></TD>
                            <TD>&nbsp;</TD><TD><INPUT NAME="password1" TYPE="password" id="password1" /></TD></TR>
			            <TR><TD><label for="fullname">Update your full name:&nbsp;</label></TD>
                            <TD>&nbsp;</TD><TD><INPUT NAME="fullname" TYPE="text" id="fullname" value="{n}" /></TD></TR>
			            <TR><TD><label for="email">Update your email address:&nbsp;</label></TD>
                            <TD>&nbsp;</TD><TD><INPUT NAME="email" TYPE="text" id="email" value="{e}" /></TD></TR>
			            <TR><TD>&nbsp;</TD><TD>&nbsp;</TD><TD>&nbsp;</TD></TR>
			            <TR><TD>&nbsp;</TD><TD><DIV class="submit">
                        <INPUT type="submit" value="Submit" /></TD><TD>&nbsp;</TD></TR>
		                </TABLE></FORM><BR></div>'''.format(bu=base_url, n=name, e=email)
    return return_data


def edit_tags(base_url, username):
    """Render tag edit functionality."""
    return_data = ''
    if request.method == 'POST' and request.forms.get('taglist') and request.forms.get('submit'):
        opt_type = request.forms.get('submit')
        if opt_type == 'DELETE':
            delete_tags(request.forms.get('taglist'))
    elif request.method == 'POST' and request.forms.get('submit'):
        return_data += '<BR>ZZZZZZZZZZZZZZZZZZZZZ<BR>'
        opt_type = request.forms.get('submit')
        return_data += '<BR>{}<BR>'.format(opt_type)
        if opt_type == 'RENAME':
            tag_rename(request.forms.get('tagname'))

    tag_list_sql = "SELECT id, tag FROM tags WHERE owner='{u}' ORDER BY tag".format(u=username)
    tag_list_qry = db_qry([tag_list_sql, None], 'select')
    if not tag_list_qry:
        return_data += 'select tags query failed:<BR>{s}<BR>'.format(s=tag_list_sql)
        return return_data
    if not tag_list_qry[0]:
        return_data += '''<BR><span class="huge">&nbsp;You do not have any tags to edit at this time.  
                          Try <A HREF="{u}add">adding</a> a bookmark to create new tags</span><BR><BR><BR>'''.format(u=base_url)
        return return_data
    return_data += '''<BR><span class="huge">Edit the tags that you wish to rename, or check the tags that you wish to delete:</span>
                        <FORM method="POST" action="{u}edit_tags" id="edit_tags">
		                <span class="normal">&nbsp;Toggle all&nbsp;</span>
                        <INPUT TYPE="checkbox" onclick="toggle('chkbox1')"><BR><BR>
		                <CENTER><div id="chkbox1"><TABLE><TR>'''.format(u=base_url)
    row_counter = 0
    max_tags_row = 4
    for row in tag_list_qry:
        tag_id = row[0]
        tag = row[1]
        return_data += '''<TD><INPUT type="checkbox" id="{i}" name="taglist[]" value="{i}" >&nbsp;<span class="big">
                              <INPUT TYPE="text" NAME="tagname[{i}]" id="tag" size="15" VALUE="{t}"></span>
                              &nbsp;&nbsp;&nbsp;<BR>&nbsp;</TD>'''.format(i=tag_id, t=tag)
        row_counter += 1
        if row_counter > max_tags_row:
            return_data += '</TR><TR>'
            row_counter = 0
    return_data += '''</TR></TABLE></DIV><INPUT type="submit" name="submit" value="DELETE" />
                      &nbsp;&nbsp;<INPUT name="submit" type="submit" value="RENAME" />
                      </CENTER></FORM><BR><BR>'''
    return return_data


def show_bmarklet(base_url):
    """Render bookmarklet content."""
    return_data = ''
    bmarklet_url = '{a}add?url='.format(a=base_url)
    bmarklet_string = """javascript:(function(){f='""" + bmarklet_url + """'+encodeURIComponent(window.location.href)+'&name='+encodeURIComponent(document.title)+'&notes='+encodeURIComponent(''+(window.getSelection?window.getSelection():document.getSelection?document.getSelection():document.selection.createRange().text));a=function(){if(!window.open(f+'noui=1&jump=doclose','d','location=yes,links=no,scrollbars=no,toolbar=no,width=550,height=550'))location.href=f+'jump=yes'};if(/Firefox/.test(navigator.userAgent)){setTimeout(a,0)}else{a()}})()"""
    return_data += '''<BR><span class="huge">&nbsp;A bookmarklet is a link that you add to your browser's Toolbar. 
                      It makes it easy to add a new bookmark to <B>Tasti</B>.</span><BR><BR>
		              Drag the link below to your toolbar, and then you can click that link when viewing any web 
                      page to quickly & easily add it as a bookmark.<BR><BR><BR>
		              <CENTER><A HREF="{b}"><B>Add to Tasti</B></a></CENTER><BR><BR><BR>'''.format(b=bmarklet_string)
    return return_data


def account_mgmt():
    """Render account management content."""
    return_data = ''
    base_url = 'http://{se}{sc}/'.format(se=request.environ.get('SERVER_NAME'), sc=request.environ.get('SCRIPT_NAME'))
    auth = auth_check()
    if auth['username'] and hash_check():
        password = ''
        name = ''
        email = ''
        fullname = ''
        username = auth['username']
        return_data += '<span class="huge"><B>Tasti Account Management</B></span><BR><BR>'
        account_sql = 'UPDATE users SET '
        if request.method == 'POST':
            # encode password and update in database
            if request.forms.get('password0') and request.forms.get('password1'):
                password0 = request.forms.get('password0').strip()
                password1 = request.forms.get('password1').strip()
                if password0 and password1 and password0 == password1:
                    password = hashlib.sha1(password0).hexdigest()
                    account_sql += "password='{p}', ".format(p=password)
            # update name in database
            if request.forms.get('fullname') and request.forms.get('fullname').strip():
                fullname = request.forms.get('fullname').strip()
                account_sql += "name='{f}', ".format(f=fullname)
            # update email in database
            if request.forms.get('email') and request.forms.get('email').strip():
                email = request.forms.get('email').strip()
                account_sql += "email='{e}', ".format(e=email)
            if password or fullname or email:
                account_sql += "username='{u}' WHERE username='{u}'".format(u=username)
                account_qry = db_qry([account_sql, None], 'update')
                if not account_qry:
                    return_data += 'Account update failed:<BR>{s}<BR>'.format(s=account_sql)
                else:
                    return_data += '<span class="big"><B><i>Update Successful</i></B></span><BR><BR>'
        # generate tab UI
        script = request.environ.get('SCRIPT_URL').split('/')[-1]
        return_data += generate_tabs()
        if script == 'account':
            return_data += account_details_form(username, base_url)
        elif script == 'import':
            if request.method == 'POST' and request.files.get('bmarks_file'):
                # process file import
                return_data += bmark_import_file()
            else:
                # show file import form
                return_data += bmark_import_form()
        elif script == 'bmarklet':
            return_data += show_bmarklet(base_url)
        elif script == 'edit_tags':
            return_data += edit_tags(base_url, username)
        else:
            return_data += '<BR>Unknown function<BR><BR>'
    else:
        return_data += '''<BR>This page is only accessible to users who have 
                            <A HREF="{h}login?do=0">logged in</a>.<BR><BR>'''.format(h=base_url)
    return return_data


def footer():
    """Footer content."""
    base_url = 'http://{se}{sc}/'.format(se=request.environ.get('SERVER_NAME'), sc=request.environ.get('SCRIPT_NAME'))
    year = year = datetime.date.today().year
    return_data = '''<span class="footer_class1">
<CENTER><A HREF="{h}">HOME</a>&nbsp;<BR><A HREF="https://github.com/netllama/tastipy">Tasti</a> is licensed under the <A HREF="http://www.gnu.org/licenses/gpl.html">GPL</a>.  Copyright {y}<BR>
</CENTER></span>'''.format(y=year, h=base_url)
    return return_data


def auth_check():
    """Check whether user is authenticated."""
    payload = {'is_authenticated': False, 'username': None}
    if request.get_cookie('tasti_username') and hash_check():
        payload['is_authenticated'] = True
        username = request.get_cookie('tasti_username').lower()
        payload['username'] = username
    return payload


def hash_check():
    """Validate password hash."""
    username = ''
    password_hash = ''
    if request.get_cookie('tasti_username'):
        username = request.get_cookie('tasti_username')
    if request.get_cookie('tasti_hash'):
        password_hash = request.get_cookie('tasti_hash')

    hash_sql = "SELECT id FROM users WHERE username='{u}' AND password='{p}'".format(u=username, p=password_hash)
    hash_qry = db_qry([hash_sql, None], 'select')
    if len(hash_qry) and hash_qry[0]:
        return hash_qry


def db_qry(sql_pl, operation):
    """Run specified query."""
    ret_val = True
    sql = sql_pl[0]
    sql_vals = sql_pl[1]
    # connect to database
    try:
        conn = psycopg2.connect(CONN_STRING)
        conn.autocommit = True
    except Exception as err:
        print 'Database connection failed due to error:\t{}'.format(err)
        return False
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    # invoke the SQL
    try:
        cursor.execute(sql, sql_vals)
        row_count = cursor.rowcount
    except Exception as err:
        # query failed
        print 'SQL ( {} )\t failed due to error:\t{}'.format(cursor.query, err)
        ret_val = False
    if operation == 'select' and ret_val:
        # get returned data to return
        ret_val = cursor.fetchall()
    cursor.close()
    conn.close()
    return ret_val
