def page_grid(page,columns=5):
    cols=max(1,int(columns));return {c:(i%cols,i//cols) for i,c in enumerate(page.components)}
