Listings
--------
A `listing` is essentially a stored search that can be rendered in a certain
style. A listing can be published to certain sites.

`Content type`, `Category` and `Content` are criteria which define the items
present in the listing. These criteria are optional and logically OR-ed.

`Count` specifies the maximum number of items in the listing.

`Style` is the default way in which the listing is rendered. The default styles are
vertical, vertical, vertical thumbnail, horizontal, promo and widget. See
`Listing styles` for detail.

`Items per page` is the number of items to display on a single listing page.

Listing styles
**************

`Vertical` is a vertical listing with no images.

`Vertical thumbnail` is a vertical listing with images.

`Horizontal` is a side-by-side listing with images. Each item looks like a
baseball trading card.

`Promo` collates the items in a slideshow.

`Widget` is the most complex. It is used when each item can be interactive, eg.
a listing of polls. Polls you have already voted on are read-only, and the
others may change content once you vote on them. The content type being
represented as a widget needs to provide code for this functionality.

