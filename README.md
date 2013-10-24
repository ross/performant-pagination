performant-pagination
=====================

**High Performance Python Django pagination**

# Overview

Performant Pagination is a (mostly) drop-in replacement for Django's built-in
Paginator that avoids problems with performance and semantic on large and/or
fast changing data sets.

# Why It's Needed

With large datasets the counting of rows to get to subsequent pages, even when
indexed, can be expensive. When asking for 10 rows starting at the 1000th many
database engines will need to scan over the first 1000 to return 1001 and on.
1000 isn't that many rows, but if it's 1M...

If you dataset is changing fast, especially faster than your walking it, you
can end up backtracking, jumping forward, or standing still. You may see some
elements many multiple times and basically what you see is undefined and
non-repeatable. If you're asking for 1000-1009 and while you're working on them
10 new rows are inserted that slot in prior to 1000, when you ask for 1010-1019
you'll see the same 10 rows again. If 10 are removed, you'll jump over what
would have been the 10 next items. If 20 are inserted, you'll backtrack and get
what was 990-999.

# How It Works

Rather than using offset and limit (count) to paginate, PerformantPaginator
uses an opaque **token** to keep track of place. Under the hood these tokens
provide information about the last item returned on the previous page and
allows it to ensure the next page picks up where the last left off. Provided
you ensure the **ordering** columns are correctly indexed the queries run by
PerformantPaginator will be able to utilize the index to walk directly to the
starting point and return the next N items.

A traversal using PerformantPaginator is guaranteed not to re-visit items
(provided they haven't changed place.) It will miss items that were inserted
after it passed a given point in the dataset. Overall the traversal is much
more deterministic and won't be affected by dataset changes.

# What You Give Up

* PerformantPaginator.count is disabled by default (returns None) it's 
  expensive to take the count of large tables on many RDBMS engines.
* Similarly the number of pages available and the "number" of the current
  page are not supported.

# What You Gain

* With proper indexing, performance and scale.

# Examples

    # order by updated descending
    qs = LargeDataSetModel.objects.all()
    paginator = PerformantPaginator(qs, per_page=40, ordering=('-updated',))
    # hand paginator off to something that takes a pagintor. it implements the
    # full page, as does Page, but some of that api may have different
    # behaviors, i.e. return None for count etc.

    # get the first page
    page = paginator.page()
    # get the second page (number is our token)
    page = pagination.page(page.next_page_number())
    # ...


    # public items, ordered by title and sub_title
    qs = LargeDataSetModel.objects.filter(public=True)
    paginator = PerformantPaginator(qs, ordering=('title', 'sub_title'))
    # ...
