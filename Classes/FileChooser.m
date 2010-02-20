//
//  FileChooser.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 25/12/09.
//  Copyright 2009 Jérôme Laheurte. All rights reserved.
//

#import "FileChooser.h"
#import "Database.h"
#import "Statement.h"
#import "CategoryViewController.h"
#import "i18n.h"

@implementation FileChooser

- initWithController:(CategoryViewController *)ctrl
{
	if (self = [super initWithNibName:@"FileChooser" bundle:[NSBundle mainBundle]])
	{
		catCtrl = ctrl;

		files = [[NSMutableArray alloc] init];
		Statement *req = [[Database connection] statementWithSQL:@"SELECT * FROM TaskCoachFile ORDER BY name COLLATE CSDIA"];
		[req execWithTarget:self action:@selector(onAddFile:)];
	}
	
	return self;
}

- (void)viewDidLoad
{
	[super viewDidLoad];

	[self setEditing:YES];
}

- (void)dealloc
{
	// Hack: if we do that before the animation is finished, the first row is not actually updated...
	[catCtrl.tableView reloadRowsAtIndexPaths:[NSArray arrayWithObject:[NSIndexPath indexPathForRow:0 inSection:0]] withRowAnimation:UITableViewRowAnimationNone];
	[files release];
	
	[super dealloc];
}

- (void)onAddFile:(NSDictionary *)dict
{
	NSMutableArray *file = [[NSMutableArray alloc] initWithCapacity:3];
	
	[file addObject:[dict objectForKey:@"id"]];
	
	if ([dict objectForKey:@"name"])
		[file addObject:[dict objectForKey:@"name"]];
	else
		[file addObject:_("Unnamed file")];

	[file addObject:[dict objectForKey:@"visible"]];
	
	[files addObject:file];
	[file release];
}

- (void)save
{
	for (NSArray *file in files)
	{
		Statement *req = [[Database connection] statementWithSQL:@"UPDATE TaskCoachFile SET visible=? WHERE id=?"];
		[req bindInteger:[[file objectAtIndex:2] intValue] atIndex:1];
		[req bindInteger:[[file objectAtIndex:0] intValue] atIndex:2];
		[req exec];
	}
}

#pragma mark Table view methods

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView {
    return 1;
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section
{
    return [files count];
}

- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath
{
    static NSString *CellIdentifier = @"Cell";
    
    UITableViewCell *cell = [tableView dequeueReusableCellWithIdentifier:CellIdentifier];
    if (cell == nil)
	{
        cell = [[[UITableViewCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:CellIdentifier] autorelease];
    }

	NSArray *file = [files objectAtIndex:indexPath.row];
	cell.textLabel.text = [file objectAtIndex:1];
	if ([[file objectAtIndex:2] intValue])
		cell.editingAccessoryType = UITableViewCellAccessoryCheckmark;
	else
		cell.editingAccessoryType = UITableViewCellAccessoryNone;

    return cell;
}

- (void)tableView:(UITableView *)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath
{
	NSInteger idx = 0;
	NSMutableArray *toReload = [[NSMutableArray alloc] initWithCapacity:2];

	for (NSMutableArray *file in files)
	{
		if ([[file objectAtIndex:2] intValue])
		{
			[file replaceObjectAtIndex:2 withObject:[NSNumber numberWithInt:0]];
			[toReload addObject:[NSIndexPath indexPathForRow:idx inSection:0]];
			break;
		}
		
		idx += 1;
	}
	
	[[files objectAtIndex:indexPath.row] replaceObjectAtIndex:2 withObject:[NSNumber numberWithInt:1]];
	[toReload addObject:indexPath];
	[Database connection].currentFile = [[files objectAtIndex:indexPath.row] objectAtIndex:0];
	
	if (indexPath.row != idx)
		[self.tableView reloadRowsAtIndexPaths:toReload withRowAnimation:UITableViewRowAnimationFade];
	[toReload release];
	
	[self save];
	
	[catCtrl loadCategories];
	[catCtrl.tableView reloadData];
	
	[catCtrl.navigationController dismissModalViewControllerAnimated:YES];
}

- (void)tableView:(UITableView *)tableView commitEditingStyle:(UITableViewCellEditingStyle)editingStyle forRowAtIndexPath:(NSIndexPath *)indexPath
{
	if (editingStyle == UITableViewCellEditingStyleDelete)
	{
		NSInteger fileId = [[[files objectAtIndex:indexPath.row] objectAtIndex:0] intValue];

		// Also delete all tasks and categories...
		[[[Database connection] statementWithSQL:[NSString stringWithFormat:@"DELETE FROM TaskHasCategory WHERE idTask IN (SELECT id FROM Task WHERE fileId=%d)", fileId]] exec];
		[[[Database connection] statementWithSQL:[NSString stringWithFormat:@"DELETE FROM TaskHasCategory WHERE idCategory IN (SELECT id FROM Category WHERE fileId=%d)", fileId]] exec];
		[[[Database connection] statementWithSQL:[NSString stringWithFormat:@"DELETE FROM Task WHERE fileId=%d", fileId]] exec];
		[[[Database connection] statementWithSQL:[NSString stringWithFormat:@"DELETE FROM Category WHERE fileId=%d", fileId]] exec];
		[[[Database connection] statementWithSQL:[NSString stringWithFormat:@"DELETE FROM TaskCoachFile WHERE id=%d", fileId]] exec];

		[self.tableView beginUpdates];

		if ([[[files objectAtIndex:indexPath.row] objectAtIndex:2] intValue])
		{
			[files removeObjectAtIndex:indexPath.row];

			// This was the current file; choose another one, if there is one
			if ([files count])
			{
				[[files objectAtIndex:0] replaceObjectAtIndex:2 withObject:[NSNumber numberWithInt:1]];
				[Database connection].currentFile = [[files objectAtIndex:0] objectAtIndex:0];
				[self.tableView reloadRowsAtIndexPaths:[NSArray arrayWithObject:[NSIndexPath indexPathForRow:0 inSection:0]] withRowAnimation:UITableViewRowAnimationFade];
			}
			else
			{
				// Huh
				[catCtrl loadCategories];
				[catCtrl.tableView reloadData];
				[catCtrl.navigationController dismissModalViewControllerAnimated:YES];
			}

		}
		else
		{
			[files removeObjectAtIndex:indexPath.row];
		}

	}

	[self.tableView deleteRowsAtIndexPaths:[NSArray arrayWithObject:indexPath] withRowAnimation:UITableViewRowAnimationFade];
	[self.tableView endUpdates];
}

@end

